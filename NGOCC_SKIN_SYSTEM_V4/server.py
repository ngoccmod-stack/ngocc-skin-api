from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unicodedata
import zipfile
import uuid
import base64
from pathlib import Path
from typing import Any

import requests
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from bs4 import BeautifulSoup
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "Resources"
AUTOMOD = ROOT / "automod"
DATA = ROOT / "data"
UPLOADS = ROOT / "uploads"
BUILDS = ROOT / "builds"
CATALOG = DATA / "skin_catalog.json"
ACTIVE = DATA / "active_resources.json"
RESOURCE_MANIFEST = DATA / "resources_manifest.json"
BUTTON_ENGINE_ZIP = ROOT / "button_engine.zip"
BUTTON_DATA = DATA / "button_resources"
BUTTON_SOURCE = BUTTON_DATA / "Source"
BUTTON_SKIN_TXT = BUTTON_DATA / "Skin" / "skin.txt"
BUTTON_DIR = BUTTON_DATA / "Button"
CLOUDINARY_FOLDER = os.environ.get("NGOCC_CLOUDINARY_FOLDER", "ngocc_resources").strip("/")
BUTTON_ENGINE_READY = BUTTON_DATA / ".engine_ready"
BUTTON_OVERRIDE_MARKER = BUTTON_DATA / ".cloud_override"
BUTTON_PREP_LOCK = threading.Lock()
BUTTON_BUILD_EXECUTOR = ThreadPoolExecutor(max_workers=1)
BUTTON_JOBS: dict[str, dict[str, Any]] = {}
BUTTON_JOBS_LOCK = threading.Lock()
def _clean_env(v: str) -> str:
    # Loại bỏ các ký tự Unicode vô hình (LRM/RLM/zero-width/BOM...) hay bị dính
    # khi copy-paste trên điện thoại, vì chúng làm hỏng HTTP header (latin-1 only).
    if not v:
        return v
    v = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060\ufeff]', '', v)
    return v.strip()

GITHUB_TOKEN = _clean_env(os.environ.get("GITHUB_TOKEN", ""))
GITHUB_REPO = _clean_env(os.environ.get("GITHUB_REPO", "ngoccmod-stack/ngocc-skin-api"))
GITHUB_BRANCH = _clean_env(os.environ.get("GITHUB_BRANCH", "main")) or "main"
GITHUB_CATALOG_PATH = _clean_env(os.environ.get("GITHUB_CATALOG_PATH", "data/skin_catalog.json")) or "data/skin_catalog.json"
CATALOG_PERSIST_LOCK = threading.Lock()
CHUNK_DIR = UPLOADS / "resource_chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

for p in (RESOURCES, DATA, UPLOADS, BUILDS, BUTTON_DATA, BUTTON_SOURCE, BUTTON_SKIN_TXT.parent, BUTTON_DIR):
    p.mkdir(parents=True, exist_ok=True)

if os.environ.get("CLOUDINARY_URL"):
    cloudinary.config(secure=True)

sys.path.insert(0, str(AUTOMOD))
from skin_catalog_scanner import find_latest_version, find_resource_versions, scan  # noqa: E402
from build_runner import build_skin as run_build  # noqa: E402

app = FastAPI(title="NGOCC Skin System API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

GARNA_MAIN = "https://lienquan.garena.vn/hoc-vien/tuong-skin/"
HEADERS = {"User-Agent": "Mozilla/5.0 (NGOCC Skin Scanner)"}


def norm(s: str) -> str:
    # "đ"/"Đ" không tự chuyển thành "d"/"D" qua NFKD (đây là 1 chữ cái riêng trong
    # tiếng Việt, không phải "d" + dấu), nếu không xử lý riêng thì encode ascii sẽ
    # XOÁ MẤT chữ này, dễ gây trùng/lệch tên giữa các tướng·skin khác nhau.
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def absurl(base: str, src: str | None) -> str:
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("http://") or src.startswith("https://"):
        return src
    from urllib.parse import urljoin
    return urljoin(base, src)


def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or r.encoding
    return r.text


def fetch_with_fallback(url: str) -> str:
    try:
        return fetch_html(url)
    except Exception:
        r = requests.get("https://r.jina.ai/http://" + url.replace("https://", "", 1), headers=HEADERS, timeout=35)
        if r.ok:
            return r.text
        raise


def extract_hero_links(main_html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(main_html, "html.parser")
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = absurl(GARNA_MAIN, a.get("href"))
        m = re.search(r"/hoc-vien/tuong-skin/d/([^/]+)/?", href)
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        text = " ".join(a.stripped_strings)
        if not text:
            img = a.find("img")
            text = (img.get("alt") if img else "") or slug
        img = a.find("img")
        thumb = absurl(GARNA_MAIN, img.get("src") if img else "")
        out.append({"slug": slug, "heroName": text.strip(), "heroImage": thumb})
        seen.add(slug)
    return out


def extract_hero_page(hero_url: str, hero_name: str) -> tuple[str, list[dict[str, str]]]:
    html = fetch_with_fallback(hero_url)
    soup = BeautifulSoup(html, "html.parser")
    # Prefer images in the content area, then fall back to document images.
    imgs = soup.find_all("img")
    hero_img = ""
    for img in imgs:
        alt = norm(img.get("alt") or "")
        src = absurl(hero_url, img.get("src"))
        if not src:
            continue
        if hero_name and norm(hero_name) in alt:
            hero_img = src
            break
    if not hero_img and imgs:
        hero_img = absurl(hero_url, imgs[0].get("src"))

    skins: list[dict[str, str]] = []
    # Ưu tiên lấy ẢNH LỚN nằm ngay dưới tên mỗi skin (ảnh chính giữa trang), theo đúng
    # yêu cầu — không dùng ảnh thumbnail nhỏ trong mục "Trang phục".
    # Lưu ý: heading thường có kèm 1 icon rank/tier (vd "S+ HỮU HẠN") nằm NGAY BÊN TRONG
    # heading đó; heading.find_next("img") mặc định sẽ dính luôn icon này (vì nó nằm
    # trong chính heading nên vẫn được coi là "next" trong cây DOM). Phải bỏ qua các
    # <img> nằm bên trong heading, chỉ lấy <img> thật sự nằm SAU heading.
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = " ".join(heading.stripped_strings).strip()
        if not text or not norm(text).startswith(norm(hero_name)):
            continue
        skin_name = re.sub(rf"^{re.escape(hero_name)}\s*", "", text, flags=re.I).strip()
        if not skin_name or norm(skin_name) in {"trang phuc", "ky nang"}:
            continue
        img = None
        for cand in heading.find_all_next("img"):
            if heading in cand.parents:
                continue  # ảnh badge/icon nằm bên trong heading, bỏ qua
            img = cand
            break
        src = absurl(hero_url, img.get("src") if img else "")
        if src:
            skins.append({"skinNameSource": skin_name, "skinImage": src})

    # Nếu không tìm được ảnh theo cách trên (trang đổi cấu trúc), rơi về mục
    # "Trang phục" (gallery nhỏ) để ít nhất vẫn có ảnh, còn hơn không có.
    if not skins:
        outfit_heading = None
        for h in soup.find_all(["h2", "h3", "h4"]):
            if norm(" ".join(h.stripped_strings)) == "trang phuc":
                outfit_heading = h
                break
        if outfit_heading is not None:
            container = outfit_heading.find_next(["ul", "ol", "div"])
            anchors = container.find_all("a", href=re.compile(r"#heroSkin-\d+")) if container else []
            for a in anchors:
                img = a.find("img")
                if not img:
                    continue
                full_name = (a.get("title") or img.get("alt") or img.get("title") or "").strip()
                src = absurl(hero_url, img.get("src"))
                if not full_name or not src:
                    continue
                skin_name = re.sub(rf"^{re.escape(hero_name)}\s*", "", full_name, flags=re.I).strip() or full_name
                skins.append({"skinNameSource": skin_name, "skinImage": src})
    # De-duplicate exact names.
    seen_names = set()
    uniq = []
    for s in skins:
        k = norm(s["skinNameSource"])
        if k and k not in seen_names:
            seen_names.add(k)
            uniq.append(s)
    return hero_img, uniq


def is_hidden_skin_name(name: str) -> bool:
    n = str(name or "").strip()
    if re.match(r"^\[\s*ex\s*\]", n, flags=re.I):
        return True
    return norm(n) in {"mac dinh", "default"}


def is_valid_hero_name(name: str) -> bool:
    n = str(name or "").strip()
    if not n:
        return False
    # Bad scanner hits such as a raw skin ID (70621) must never become hero cards.
    if re.fullmatch(r"\d{4,6}", n):
        return False
    return True


def is_valid_hero_id(hero_id: str) -> bool:
    try:
        v = int(str(hero_id or "").strip())
    except Exception:
        return False
    return 100 <= v <= 999


def sanitize_catalog(data: dict[str, Any]) -> dict[str, Any]:
    """Remove stale/rubbish hero entries from older catalogs and dedupe heroes/skins."""
    out = dict(data or {})
    merged: dict[str, dict] = {}
    order: list[str] = []
    for h in out.get("heroes", []):
        hid = str(h.get("heroId", "")).strip()
        hname = str(h.get("heroName", "")).strip()
        if not is_valid_hero_id(hid) or not is_valid_hero_name(hname):
            continue
        key = norm(hname) or hid
        if key not in merged:
            merged[key] = dict(h)
            merged[key]["heroId"] = hid
            merged[key]["heroName"] = hname
            merged[key]["skins"] = []
            order.append(key)
        target = merged[key]
        seen = {str(x.get("skinId")) for x in target.get("skins", [])}
        for sk in h.get("skins", []):
            sid = str(sk.get("skinId", "")).strip()
            sname = str(sk.get("skinName", "")).strip()
            if not sid or sid in seen or is_hidden_skin_name(sname):
                continue
            seen.add(sid)
            target["skins"].append(dict(sk))
    heroes = [merged[k] for k in order]
    for h in heroes:
        h["skinCount"] = len(h.get("skins", []))
    out["heroes"] = heroes
    out["heroCount"] = len(heroes)
    out["skinCount"] = sum(len(h.get("skins", [])) for h in heroes)
    return out


def filter_auto_catalog(auto_data: dict[str, Any]) -> dict[str, Any]:
    out = dict(auto_data)
    heroes = []
    seen_heroes: set[str] = set()
    for h in auto_data.get("heroes", []):
        name = str(h.get("heroName", "")).strip()
        if not is_valid_hero_id(str(h.get("heroId", ""))) or not is_valid_hero_name(name):
            continue
        hk = norm(name) or str(h.get("heroId", ""))
        if hk in seen_heroes:
            continue
        seen_heroes.add(hk)
        hh = dict(h)
        skins = []
        seen_skins: set[str] = set()
        for sk in h.get("skins", []):
            sid = str(sk.get("skinId", "")).strip()
            sname = str(sk.get("skinName", "")).strip()
            if is_hidden_skin_name(sname):
                continue
            if not sid or sid in seen_skins:
                continue
            seen_skins.add(sid)
            skins.append(dict(sk))
        hh["skins"] = skins
        heroes.append(hh)
    out["heroes"] = heroes
    out["heroCount"] = len(heroes)
    out["skinCount"] = sum(len(h.get("skins", [])) for h in heroes)
    return out


def merge_manual_skins(catalog_data: dict[str, Any], old_data: dict[str, Any]) -> dict[str, Any]:
    """Preserve skins that the admin manually added and that the official scanner cannot see."""
    if not isinstance(old_data, dict):
        return catalog_data
    old_by_hero = {str(h.get("heroId", "")).strip(): h for h in old_data.get("heroes", [])}
    for hero in catalog_data.get("heroes", []):
        old_hero = old_by_hero.get(str(hero.get("heroId", "")).strip())
        if not old_hero:
            continue
        existing = {str(x.get("skinId", "")).strip() for x in hero.get("skins", [])}
        for skin in old_hero.get("skins", []):
            if not skin.get("manualAdded"):
                continue
            sid = str(skin.get("skinId", "")).strip()
            if not sid or sid in existing or is_hidden_skin_name(str(skin.get("skinName", ""))):
                continue
            if not re.fullmatch(r"\d{5}", sid):
                continue
            hero.setdefault("skins", []).append(dict(skin))
            existing.add(sid)
        hero["skinCount"] = len(hero.get("skins", []))
    catalog_data["skinCount"] = sum(len(h.get("skins", [])) for h in catalog_data.get("heroes", []))
    return catalog_data


def merge_catalog(auto_data: dict[str, Any], garena_heroes: list[dict[str, str]]) -> dict[str, Any]:
    auto_data = filter_auto_catalog(auto_data)
    by_name = {norm(h.get("heroName", "")): h for h in garena_heroes if is_valid_hero_name(h.get("heroName", ""))}
    result = {
        "schemaVersion": 3,
        "resourcesVersion": auto_data.get("resourcesVersion", ""),
        "generatedAt": auto_data.get("generatedAt", ""),
        "heroCount": 0,
        "skinCount": 0,
        "heroes": [],
    }
    by_hero_key: dict[str, dict] = {}
    for h in auto_data.get("heroes", []):
        hero_id = str(h.get("heroId", "")).strip()
        hero_name = str(h.get("heroName", "")).strip()
        g = by_name.get(norm(hero_name))
        # When official Garena data is available, accept only heroes actually present there.
        if not g:
            continue
        key = norm(hero_name) or hero_id
        hero = by_hero_key.get(key)
        if hero is None:
            hero = {
                "heroId": hero_id,
                "heroName": hero_name,
                "heroImage": g.get("heroImage", ""),
                "garenaSlug": g.get("slug", ""),
                "skins": [],
            }
            by_hero_key[key] = hero
            result["heroes"].append(hero)
        seen_skin_ids = {str(x.get("skinId")) for x in hero["skins"]}
        for s in h.get("skins", []):
            sid = str(s.get("skinId", "")).strip()
            sname = str(s.get("skinName", "")).strip()
            if not sid or sid in seen_skin_ids or is_hidden_skin_name(sname):
                continue
            seen_skin_ids.add(sid)
            hero["skins"].append({
                "skinId": sid,
                "skinName": sname,
                "skinImage": "",
                "supported": bool(s.get("resolved")),
                "resourcesVersion": s.get("resourcesVersion", result["resourcesVersion"]),
            })

    # Match skin images by normalized source name; never by position.
    for hero in result["heroes"]:
        garena = next((x for x in garena_heroes if x.get("slug") == hero.get("garenaSlug")), None)
        if not garena or not garena.get("_skins"):
            continue
        source_skins = [x for x in garena["_skins"] if not is_hidden_skin_name(x.get("skinNameSource", ""))]
        by_skin_name: dict[str, list[dict[str, str]]] = {}
        for x in source_skins:
            by_skin_name.setdefault(norm(x["skinNameSource"]), []).append(x)
        used_images: set[str] = set()
        for skin in hero["skins"]:
            key = norm(skin["skinName"])
            img = ""
            for c in by_skin_name.get(key, []):
                if c.get("skinImage") and c["skinImage"] not in used_images:
                    img = c["skinImage"]
                    break
            if not img and key:
                best = None
                for c in source_skins:
                    if c.get("skinImage") in used_images:
                        continue
                    ck = norm(c.get("skinNameSource", ""))
                    if ck and (ck in key or key in ck):
                        if best is None or len(ck) > len(norm(best.get("skinNameSource", ""))):
                            best = c
                if best:
                    img = best.get("skinImage", "")
            if img:
                used_images.add(img)
            skin["skinImage"] = img
            if not img:
                skin["imageMissing"] = True
        hero["skinCount"] = len(hero["skins"])

    result["heroCount"] = len(result["heroes"])
    result["skinCount"] = sum(len(h.get("skins", [])) for h in result["heroes"])
    return result


def load_json(path: Path, default: Any):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def cloudinary_ready() -> bool:
    return bool(os.environ.get("CLOUDINARY_URL"))


def github_ready() -> bool:
    return bool(GITHUB_TOKEN and GITHUB_REPO)


def github_api_headers() -> dict[str, str]:
    if not github_ready():
        raise RuntimeError("GitHub storage chưa được cấu hình.")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_catalog_read() -> dict[str, Any]:
    if not github_ready():
        return {}
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_CATALOG_PATH}"
    r = requests.get(url, headers=github_api_headers(), params={"ref": GITHUB_BRANCH}, timeout=30)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    payload = r.json()
    content = payload.get("content", "")
    if not content:
        return {}
    raw = base64.b64decode(content.replace("\n", ""))
    data = json.loads(raw.decode("utf-8"))
    if isinstance(data, dict):
        data["_github_sha"] = payload.get("sha", "")
        return data
    return {}


def github_catalog_write(data: dict[str, Any]) -> None:
    if not github_ready():
        return
    clean = dict(data)
    clean.pop("_github_sha", None)
    raw = json.dumps(clean, ensure_ascii=False, indent=2).encode("utf-8")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_CATALOG_PATH}"
    sha = ""
    try:
        r = requests.get(url, headers=github_api_headers(), params={"ref": GITHUB_BRANCH}, timeout=30)
        if r.status_code == 200:
            sha = r.json().get("sha", "")
        elif r.status_code != 404:
            r.raise_for_status()
    except Exception:
        raise
    body = {
        "message": "chore: persist NGOCC skin catalog",
        "content": base64.b64encode(raw).decode("ascii"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        body["sha"] = sha
    r = requests.put(url, headers={**github_api_headers(), "Content-Type": "application/json"}, json=body, timeout=60)
    r.raise_for_status()


def resource_public_id(version: str) -> str:
    # Raw public IDs must include the extension.
    return f"{CLOUDINARY_FOLDER}/{version}.zip"


def catalog_public_id() -> str:
    return f"{CLOUDINARY_FOLDER}/skin_catalog.json"


def catalog_secure_url() -> str:
    if not cloudinary_ready():
        return ""
    try:
        return cloudinary.utils.cloudinary_url(catalog_public_id(), resource_type="raw", type="upload", secure=True)[0]
    except Exception:
        return ""


def persist_catalog_to_cloud(data: dict[str, Any]) -> str:
    warnings = []
    if cloudinary_ready():
        try:
            local = DATA / "skin_catalog.json"
            local.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            cloudinary.uploader.upload(
                str(local), resource_type="raw", public_id=catalog_public_id(), overwrite=True
            )
        except Exception as e:
            warnings.append(f"Cloudinary: {e}")
    if github_ready():
        try:
            with CATALOG_PERSIST_LOCK:
                github_catalog_write(data)
        except Exception as e:
            warnings.append(f"GitHub: {e}")
    if warnings:
        return " | ".join(warnings)
    return catalog_secure_url() if cloudinary_ready() else ""


def restore_catalog_from_cloud() -> dict[str, Any]:
    # GitHub is the durable fallback for Render/other ephemeral filesystems.
    if github_ready():
        try:
            g = github_catalog_read()
            if g:
                g.pop("_github_sha", None)
                save_json(CATALOG, g)
                return g
        except Exception:
            pass
    url = catalog_secure_url()
    if not url:
        return {}
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        data = r.json()
        save_json(CATALOG, data)
        return data
    except Exception:
        return {}


def build_public_id(skin_id: str, version: str) -> str:
    return f"{CLOUDINARY_FOLDER}/builds/{version}/{skin_id}.zip"


def build_secure_url(skin_id: str, version: str) -> str:
    if not cloudinary_ready():
        return ""
    try:
        return cloudinary.utils.cloudinary_url(
            build_public_id(skin_id, version), resource_type="raw", type="upload", secure=True
        )[0]
    except Exception:
        return ""


def persist_build_to_cloud(path: Path, skin_id: str, version: str) -> None:
    if not path.is_file():
        return
    errors=[]
    if cloudinary_ready():
        try:
            cloudinary.uploader.upload(
                str(path), resource_type="raw", public_id=build_public_id(skin_id, version), overwrite=True
            )
            return
        except Exception as e:
            errors.append(f"Cloudinary: {e}")
    if github_ready():
        try:
            github_upload_build_asset(version, skin_id, path)
            return
        except Exception as e:
            errors.append(f"GitHub: {e}")
    if errors:
        raise RuntimeError("; ".join(errors))


def restore_build_from_cloud(skin_id: str, version: str) -> Path | None:
    if not version:
        return None
    target = BUILDS / f"{skin_id}_{version}.zip"
    urls=[]
    if cloudinary_ready():
        u=build_secure_url(skin_id, version)
        if u: urls.append((u, HEADERS))
    if github_ready():
        try:
            u=github_find_build_asset(version, skin_id)
            if u: urls.append((u, {**github_headers(), "Accept":"application/octet-stream"}))
        except Exception:
            pass
    for url, headers in urls:
        try:
            r=requests.get(url, headers=headers, timeout=1800, stream=True)
            r.raise_for_status()
            with target.open("wb") as f:
                for ch in r.iter_content(1024 * 1024):
                    if ch:
                        f.write(ch)
            if target.is_file() and target.stat().st_size > 0:
                return target
        except Exception:
            target.unlink(missing_ok=True)
    return None



def resource_secure_url(version: str) -> str:
    if not cloudinary_ready():
        return ""
    try:
        return cloudinary.utils.cloudinary_url(
            resource_public_id(version),
            resource_type="raw",
            type="upload",
            secure=True,
        )[0]
    except Exception:
        return ""


def load_resource_manifest() -> dict[str, Any]:
    return load_json(RESOURCE_MANIFEST, {"versions": {}, "active": ""})


def save_resource_manifest(data: dict[str, Any]) -> None:
    save_json(RESOURCE_MANIFEST, data)


def ensure_local_resources_from_cloud(version: str | None = None) -> str:
    versions = find_resource_versions(RESOURCES)
    if version:
        local=RESOURCES/version
        if (local/"Databin/Client/Actor/heroSkin.bytes").is_file(): return version
    elif versions:
        return versions[-1].name
    manifest=load_resource_manifest(); target=version or manifest.get('active') or ''
    if not target and github_ready():
        try:
            rr=requests.get(f'https://api.github.com/repos/{GITHUB_REPO}/releases', headers=github_headers(), params={'per_page':100}, timeout=30)
            rr.raise_for_status()
            tags=[str(x.get('tag_name',''))[10:] for x in rr.json() if str(x.get('tag_name','')).startswith('resources-')]
            if tags:
                target=sorted(tags, key=version_key)[-1]
        except Exception:
            pass
    if not target: raise FileNotFoundError('Chưa có Resources; Admin hãy cập nhật Resources trước.')
    info=manifest.get('versions',{}).get(target) or {}
    asset_url=info.get('assetUrl')
    if not asset_url:
        # Try resolving from release tag.
        if not github_ready(): raise FileNotFoundError('Chưa cấu hình GitHub để khôi phục Resources.')
        h=github_headers(); base=f'https://api.github.com/repos/{GITHUB_REPO}/releases/tags/resources-{target}'
        r=requests.get(base,headers=h,timeout=30); r.raise_for_status(); rel=r.json();
        asset=next((a for a in rel.get('assets',[]) if a.get('name')==f'Resources-{target}.zip'),None)
        if not asset: raise FileNotFoundError(f'Không tìm thấy Resources {target} trong GitHub Release.')
        asset_url=asset['url']
    local_zip=UPLOADS/f'restore_{target}.zip'
    try:
        github_download_asset(asset_url,local_zip)
        cp=subprocess.run([sys.executable,str(AUTOMOD/'resource_manager.py'),'--resources',str(RESOURCES),'install',str(local_zip)],cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
        if cp.returncode!=0: raise RuntimeError(cp.stderr or cp.stdout or 'Không thể khôi phục Resources')
        m=re.search(r'Installed Resources version:\s*(.+)',cp.stdout)
        return m.group(1).strip() if m else target
    finally: local_zip.unlink(missing_ok=True)


@app.get("/api/resources/status")
def resources_status():
    manifest = load_resource_manifest()
    local_versions = [p.name for p in find_resource_versions(RESOURCES)]
    return {
        "ok": True,
        "active": manifest.get("active", ""),
        "versions": manifest.get("versions", {}),
        "localVersions": local_versions,
    }


@app.get("/api/health")
def health():
    current = load_json(ACTIVE, {})
    return {"ok": True, "resourcesVersion": current.get("version", "")}



# ===================== MOD NÚT BẤM THƯỜNG =====================
def _button_engine_extract(force: bool = False) -> None:
    """Lazily unpack only the fixed engine pieces from the supplied button tool."""
    with BUTTON_PREP_LOCK:
        if BUTTON_ENGINE_READY.exists() and not force and (BUTTON_SOURCE / 'personalbuttoneffect_10618.assetbundle').exists():
            return
        if not BUTTON_ENGINE_ZIP.is_file():
            raise FileNotFoundError('Thiếu button_engine.zip')
        tmp = BUTTON_DATA.with_name('button_resources_tmp')
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(BUTTON_ENGINE_ZIP) as z:
            prefix = '#1Nút Bấm/'
            members = z.namelist()
            wanted_prefixes = (prefix + 'core/', prefix + 'lib/', prefix + 'Button/', prefix + 'Skin/')
            for name in members:
                if not name.startswith(wanted_prefixes):
                    continue
                rel = name[len(prefix):]
                if not rel or rel.endswith('/') or '/__pycache__/' in rel or rel.endswith('.pyc'):
                    continue
                dest = tmp / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(z.read(name))
            # Seed Source from the exact supplied button tool unless a persisted source exists.
            src_members = [n for n in members if n.startswith(prefix+'Source/') and not n.endswith('/')]
            if src_members:
                for name in src_members:
                    rel = name[len(prefix+'Source/'):]
                    if '/__pycache__/' in rel or rel.endswith('.pyc'):
                        continue
                    dest = tmp/'Source'/rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(z.read(name))
            # Move into live location atomically-ish.
        if BUTTON_DATA.exists():
            for child in BUTTON_DATA.iterdir():
                if child.name.startswith('.'):
                    continue
                if child.name == tmp.name:
                    continue
                if child.is_dir(): shutil.rmtree(child, ignore_errors=True)
                else:
                    try: child.unlink()
                    except Exception: pass
        for child in tmp.iterdir():
            shutil.move(str(child), str(BUTTON_DATA/child.name))
        shutil.rmtree(tmp, ignore_errors=True)
        BUTTON_ENGINE_READY.write_text('1', encoding='utf-8')


def _button_cloud_public_id() -> str:
    return f"{CLOUDINARY_FOLDER}/button_resources.zip"


def _button_cloud_url() -> str:
    if not cloudinary_ready(): return ''
    try:
        return cloudinary.utils.cloudinary_url(_button_cloud_public_id(), resource_type='raw', type='upload', secure=True)[0]
    except Exception:
        return ''


def _persist_button_resources_cloud() -> str:
    try:
        local = DATA / 'button_resources.zip'
        with zipfile.ZipFile(local, 'w', zipfile.ZIP_DEFLATED) as z:
            for base_name in ['Source','Skin','Button']:
                base = BUTTON_DATA/base_name
                if not base.is_dir(): continue
                for f in base.rglob('*'):
                    if f.is_file(): z.write(f, f'{base_name}/{f.relative_to(base).as_posix()}')
        if cloudinary_ready():
            cloudinary.uploader.upload(str(local), resource_type='raw', public_id=_button_cloud_public_id(), overwrite=True)
        return ''
    except Exception as e:
        return str(e)


def _restore_button_resources_cloud() -> bool:
    url=_button_cloud_url()
    if not url: return False
    try:
        tmp=UPLOADS/'button_resources_restore.zip'
        r=requests.get(url, headers=HEADERS, timeout=300)
        r.raise_for_status(); tmp.write_bytes(r.content)
        extract=UPLOADS/'button_restore_extract'
        shutil.rmtree(extract, ignore_errors=True); extract.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(tmp) as z: z.extractall(extract)
        ok=False
        for base_name in ['Source','Skin','Button']:
            src=extract/base_name
            if src.is_dir():
                dst=BUTTON_DATA/base_name
                shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src,dst,dirs_exist_ok=True); ok=True
        if ok: BUTTON_ENGINE_READY.write_text('1',encoding='utf-8')
        return ok
    except Exception:
        return False


def ensure_button_resources() -> None:
    _button_engine_extract(False)
    # On a fresh Render instance, restore the admin-updated source from durable storage.
    # Do not overwrite the live files on every request.
    if not BUTTON_OVERRIDE_MARKER.exists():
        if _restore_button_resources_cloud():
            BUTTON_OVERRIDE_MARKER.write_text('1', encoding='utf-8')


def _button_skin_parser(path: Path) -> dict[str, tuple[str, str]]:
    out={}; hero=''
    id_re=re.compile(r'^\s*(\d{4,6})\s*[-–—:]\s*(.+?)\s*$')
    hero_re=re.compile(r'^\s*(\S.*?)\s*:\s*$')
    if not path.is_file(): return out
    for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
        m=id_re.match(line)
        if m:
            out[m.group(1)]=(m.group(2),hero); continue
        m=hero_re.match(line)
        if m and m.group(1) and not m.group(1)[0].isdigit(): hero=m.group(1)
    return out


def _button_scan_source(src: Path) -> dict[str,dict]:
    res={}
    pat=re.compile(r'^personalbutton(effect|sprite)_(\d+)(_raw)?\.assetbundle$',re.I)
    for p in src.rglob('*.assetbundle') if src.is_dir() else []:
        m=pat.match(p.name)
        if not m: continue
        kind,sid,raw=m.group(1).lower(),m.group(2),bool(m.group(3))
        d=res.setdefault(sid,{'effect':None,'effect_raw':None,'sprite_raw':None})
        if kind=='effect': d['effect_raw' if raw else 'effect']=str(p)
        elif kind=='sprite' and raw: d['sprite_raw']=str(p)
    return res


def _button_catalog() -> dict:
    ensure_button_resources()
    skins=_button_skin_parser(BUTTON_SKIN_TXT)
    files=_button_scan_source(BUTTON_SOURCE)
    hero_by_prefix={}
    for sid,(name,hero) in skins.items():
        if hero and len(sid)>=3: hero_by_prefix.setdefault(sid[:3],hero)
    rows=[]
    for sid,f in files.items():
        if not (f.get('effect') or f.get('sprite_raw')): continue
        if sid in skins: name,hero,known=skins[sid][0],skins[sid][1],True
        else:
            hero=hero_by_prefix.get(sid[:3],'') if len(sid)>=3 else ''
            name=f'Skin {sid}?' ; known=False
        parts=[]
        if f.get('effect'): parts.append('FX')
        if f.get('sprite_raw'): parts.append('JOY')
        rows.append({'id':sid,'name':name,'hero':hero,'parts':'+'.join(parts) or '-', 'known':known})
    rows.sort(key=lambda r:(r['hero'].lower(), not r['known'], int(r['id'])))
    return {'ready':bool(rows),'count':len(rows),'rows':rows}


class ButtonSourceUploadInfo(BaseModel):
    pass


@app.get('/api/button/catalog')
def button_catalog():
    try:
        return {'ok':True, **_button_catalog()}
    except Exception as e:
        raise HTTPException(500, f'Không tải được danh sách Nút Bấm: {e}')


@app.post('/api/button/resources/upload')
async def button_resources_upload(file: UploadFile = File(...)):
    try:
        ensure_button_resources()
        raw=UPLOADS/f'button_upload_{uuid.uuid4().hex}.zip'
        with raw.open('wb') as f:
            while ch:=await file.read(1024*1024): f.write(ch)
        extract=UPLOADS/f'button_upload_extract_{uuid.uuid4().hex}'
        extract.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(raw) as z:
            z.extractall(extract)
        # Accept Source.zip, full button tool zip, or a ZIP whose root directly contains personalbutton*.assetbundle.
        src_candidates=[p for p in extract.rglob('*') if p.is_dir() and p.name.lower()=='source']
        if src_candidates:
            source_dir=src_candidates[0]
        else:
            direct=extract
            root_children=[p for p in extract.iterdir()]
            top_dirs=[p for p in root_children if p.is_dir()]
            if len(top_dirs)==1 and (top_dirs[0]/'Source').is_dir():
                source_dir=top_dirs[0]/'Source'
            else:
                source_dir=direct
        found=list(source_dir.glob('personalbutton*.assetbundle')) if source_dir.is_dir() else []
        if not found:
            found=list(source_dir.rglob('personalbutton*.assetbundle')) if source_dir.is_dir() else []
        if not found: raise HTTPException(400,'ZIP không có personalbutton*.assetbundle trong Source.')
        # Replace only Source. If full tool includes Skin/skin.txt, update names too.
        shutil.rmtree(BUTTON_SOURCE,ignore_errors=True); BUTTON_SOURCE.mkdir(parents=True,exist_ok=True)
        for p in source_dir.rglob('*'):
            if p.is_file() and p.name.lower().endswith('.assetbundle'):
                rel=p.relative_to(source_dir); d=BUTTON_SOURCE/rel; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d)
        for p in extract.rglob('skin.txt'):
            BUTTON_SKIN_TXT.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,BUTTON_SKIN_TXT); break
        # If full tool ZIP includes Button/ base bundles, accept those as updated base as well.
        for bd in extract.rglob('Button'):
            if bd.is_dir() and (bd/'battleotherui.assetbundle').is_file():
                shutil.rmtree(BUTTON_DIR,ignore_errors=True); shutil.copytree(bd,BUTTON_DIR,dirs_exist_ok=True); break
        BUTTON_ENGINE_READY.write_text('1',encoding='utf-8')
        warn=_persist_button_resources_cloud()
        if not warn:
            BUTTON_OVERRIDE_MARKER.write_text('1', encoding='utf-8')
        shutil.rmtree(extract,ignore_errors=True)
        try: raw.unlink()
        except Exception: pass
        cat=_button_catalog()
        return {'ok':True,'cloudWarning':warn,**cat}
    except HTTPException: raise
    except zipfile.BadZipFile:
        raise HTTPException(400,'File tải lên không phải ZIP hợp lệ.')
    except Exception as e:
        raise HTTPException(500,f'Cập nhật Resources Nút Bấm thất bại: {e}')


def _button_build_sync(skin_id: str, job_id: str | None = None):
    import importlib, sys as _sys, traceback
    try:
        ensure_button_resources()
        cat=_button_catalog()
        row=next((r for r in cat['rows'] if str(r['id'])==str(skin_id)),None)
        if not row:
            raise HTTPException(404,'Nút bấm ID chưa có trong Resources.')
        files=_button_scan_source(BUTTON_SOURCE).get(str(skin_id))
        if not files:
            raise HTTPException(404,'Không tìm thấy Source cho ID nút này.')
        if not (BUTTON_DIR/'battleotherui.assetbundle').is_file():
            raise HTTPException(409,'Thiếu Button/battleotherui.assetbundle.')

        # Luôn ưu tiên đúng engine bundled trong button_resources; tránh collision với
        # module tên "core" của package khác đã import trước đó.
        button_root = str(BUTTON_DATA)
        if button_root not in _sys.path:
            _sys.path.insert(0, button_root)
        for _name in [x for x in list(_sys.modules) if x == 'core' or x.startswith('core.')]:
            _sys.modules.pop(_name, None)
        graft_mod=importlib.import_module('core.graft')

        out_dir=BUILDS/'buttons'/str(skin_id)
        shutil.rmtree(out_dir, ignore_errors=True)
        work=out_dir/'Resources'/'1.63.1'/'assetbundle'/'uisystem'/'battle'
        work.mkdir(parents=True,exist_ok=True)
        out_bundle=work/'battleotherui.assetbundle'
        logs=[]
        if job_id:
            with BUTTON_JOBS_LOCK:
                BUTTON_JOBS[job_id].update(progress='Đang graft FX + joystick...', log=[])

        graft_mod.build_one(
            str(skin_id), files, str(BUTTON_DIR/'battleotherui.assetbundle'), str(out_bundle),
            log=logs.append, step=lambda: None,
            button_dir=str(BUTTON_DIR), out_dir=str(work)
        )
        raw_src=BUTTON_DIR/'battleotherui_raw.assetbundle'
        if raw_src.is_file():
            shutil.copy2(raw_src,work/'battleotherui_raw.assetbundle')
        pack_name=(row.get('hero','')+' '+row.get('name','')).strip() or str(skin_id)
        pack_name=re.sub(r'[\\/:*?"<>|]','',pack_name).strip() or str(skin_id)
        zip_path=BUILDS/f'button_{skin_id}.zip'
        tmp=zip_path.with_suffix('.tmp')
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
            for f in work.rglob('*'):
                if not f.is_file(): continue
                rel=f.relative_to(out_dir).as_posix()
                z.write(f,f'{pack_name}/files/{rel}')
        tmp.replace(zip_path)
        if job_id:
            with BUTTON_JOBS_LOCK:
                BUTTON_JOBS[job_id].update(status='done', progress='Hoàn tất', file=str(zip_path), filename=f'{pack_name}.zip', log=logs[-80:])
        return zip_path, f'{pack_name}.zip', logs
    except HTTPException as e:
        if job_id:
            with BUTTON_JOBS_LOCK:
                BUTTON_JOBS[job_id].update(status='error', error=e.detail if isinstance(e.detail,str) else str(e.detail))
        raise
    except Exception as e:
        detail=f'{type(e).__name__}: {e}'
        if job_id:
            with BUTTON_JOBS_LOCK:
                BUTTON_JOBS[job_id].update(status='error', error=detail, log=logs[-80:] if 'logs' in locals() else [])
        raise RuntimeError(detail + ('\n' + '\n'.join(logs[-40:]) if 'logs' in locals() and logs else '')) from e


@app.post('/api/button/build/start/{skin_id}')
def start_button_build(skin_id: str):
    # Kiểm tra nhanh trước khi đưa build nặng sang background worker.
    ensure_button_resources()
    cat=_button_catalog()
    row=next((r for r in cat['rows'] if str(r['id'])==str(skin_id)),None)
    if not row:
        raise HTTPException(404,'Nút bấm ID chưa có trong Resources.')
    files=_button_scan_source(BUTTON_SOURCE).get(str(skin_id))
    if not files:
        raise HTTPException(404,'Không tìm thấy Source cho ID nút này.')
    job_id=uuid.uuid4().hex
    with BUTTON_JOBS_LOCK:
        BUTTON_JOBS[job_id]={'status':'queued','skinId':str(skin_id),'progress':'Đang xếp hàng...', 'error':'', 'file':'', 'filename':'', 'log':[]}
    def runner():
        with BUTTON_JOBS_LOCK:
            BUTTON_JOBS[job_id]['status']='running'
            BUTTON_JOBS[job_id]['progress']='Đang tạo ZIP...'
        try:
            _button_build_sync(str(skin_id), job_id=job_id)
        except Exception:
            # _button_build_sync already records the useful error.
            pass
    BUTTON_BUILD_EXECUTOR.submit(runner)
    return {'ok':True,'jobId':job_id,'skinId':str(skin_id)}


@app.get('/api/button/build/status/{job_id}')
def button_build_status(job_id: str):
    with BUTTON_JOBS_LOCK:
        job=BUTTON_JOBS.get(job_id)
        if not job:
            raise HTTPException(404,'Không tìm thấy phiên build.')
        return {'ok':True, **{k:v for k,v in job.items() if k != 'file'}}


@app.get('/api/button/build/download/{job_id}')
def button_build_download(job_id: str):
    with BUTTON_JOBS_LOCK:
        job=BUTTON_JOBS.get(job_id)
        if not job:
            raise HTTPException(404,'Không tìm thấy phiên build.')
        if job.get('status') != 'done':
            raise HTTPException(409,job.get('error') or 'ZIP chưa tạo xong.')
        file_path=job.get('file',''); filename=job.get('filename') or (f'Nút Bấm {job.get("skinId")}.zip')
    if not file_path or not Path(file_path).is_file():
        raise HTTPException(404,'File ZIP không còn trên server.')
    return FileResponse(file_path,filename=filename,media_type='application/zip')


# Endpoint cũ vẫn giữ để tương thích; nó dùng cùng builder nhưng có thể chịu timeout ở
# proxy nếu build quá lâu. Frontend mới dùng start/status/download ở trên.
@app.post('/api/button/build/{skin_id}')
def build_button(skin_id: str):
    try:
        zip_path, filename, _ = _button_build_sync(str(skin_id))
        return FileResponse(str(zip_path),filename=filename,media_type='application/zip')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500,f'Tạo mod Nút Bấm thất bại: {e}')

@app.get("/api/catalog")
def catalog():
    data = load_json(CATALOG, {})
    if not data and (cloudinary_ready() or github_ready()):
        data = restore_catalog_from_cloud()
    if not data:
        return JSONResponse({"ready": False, "heroes": [], "skinCount": 0})
    clean = sanitize_catalog(data)
    if clean != data:
        save_json(CATALOG, clean)
        try: persist_catalog_to_cloud(clean)
        except Exception: pass
        data = clean
    return JSONResponse({"ready": True, **data})



def github_headers():
    if not GITHUB_TOKEN:
        raise RuntimeError("Chưa cấu hình GITHUB_TOKEN trên Render.")
    return {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def github_create_or_get_release(version: str):
    h=github_headers(); base=f"https://api.github.com/repos/{GITHUB_REPO}"
    tag=f"resources-{version}"
    r=requests.get(f"{base}/releases/tags/{tag}",headers=h,timeout=30)
    if r.status_code==200: return r.json()
    if r.status_code!=404: r.raise_for_status()
    r=requests.post(f"{base}/releases",headers={**h,"Content-Type":"application/json"},json={"tag_name":tag,"name":f"Resources {version}","body":f"NGOCC Resources {version}","draft":False,"prerelease":False},timeout=30)
    r.raise_for_status(); return r.json()


def github_upload_asset(version: str, zip_path: Path):
    rel=github_create_or_get_release(version)
    # Remove old same-name asset if present.
    asset_name=f"Resources-{version}.zip"
    h=github_headers()
    for a in rel.get("assets",[]):
        if a.get("name")==asset_name:
            rr=requests.delete(a["url"],headers=h,timeout=30)
            if rr.status_code not in (204,404): rr.raise_for_status()
            break
    up_url=rel["upload_url"].split("{",1)[0] + "?name=" + asset_name
    with zip_path.open("rb") as fh:
        rr=requests.post(up_url,headers={**h,"Content-Type":"application/zip"},data=fh,timeout=1800)
    rr.raise_for_status()
    return rr.json()


def github_download_asset(asset_url: str, dest: Path):
    h={**github_headers(),"Accept":"application/octet-stream"}
    r=requests.get(asset_url,headers=h,timeout=1800,stream=True)
    r.raise_for_status()
    with dest.open("wb") as f:
        for ch in r.iter_content(1024*1024):
            if ch: f.write(ch)


def github_upload_build_asset(version: str, skin_id: str, zip_path: Path):
    """Durable fallback for generated AutoMod ZIPs when Cloudinary is unavailable."""
    rel=github_create_or_get_release(version)
    asset_name=f"Skin-{skin_id}.zip"
    h=github_headers()
    for a in rel.get("assets", []):
        if a.get("name") == asset_name:
            rr=requests.delete(a["url"], headers=h, timeout=30)
            if rr.status_code not in (204,404): rr.raise_for_status()
            break
    up_url=rel["upload_url"].split("{",1)[0] + "?name=" + asset_name
    with zip_path.open("rb") as fh:
        rr=requests.post(up_url, headers={**h,"Content-Type":"application/zip"}, data=fh, timeout=1800)
    rr.raise_for_status()
    return rr.json()


def github_find_build_asset(version: str, skin_id: str) -> str:
    if not github_ready():
        return ""
    h=github_headers(); url=f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/resources-{version}"
    r=requests.get(url, headers=h, timeout=30)
    if r.status_code != 200:
        return ""
    rel=r.json()
    asset_name=f"Skin-{skin_id}.zip"
    asset=next((a for a in rel.get("assets", []) if a.get("name")==asset_name), None)
    return asset.get("url", "") if asset else ""


@app.post("/api/resources/upload/init")
def resources_upload_init():
    sid=uuid.uuid4().hex
    (CHUNK_DIR/sid).mkdir(parents=True,exist_ok=True)
    return {"ok":True,"uploadId":sid,"chunkSize":8*1024*1024}


@app.post("/api/resources/upload/chunk")
async def resources_upload_chunk(uploadId: str, index: int, file: UploadFile = File(...)):
    d=CHUNK_DIR/uploadId
    if not d.is_dir(): raise HTTPException(404,"Upload session không tồn tại hoặc đã hết hạn.")
    target=d/f"{int(index):08d}.part"
    try:
        with target.open("wb") as f:
            while ch:=await file.read(1024*1024): f.write(ch)
        return {"ok":True,"index":int(index)}
    except Exception as e:
        raise HTTPException(500,f"Lưu chunk thất bại: {e}")


@app.post("/api/resources/upload/finalize")
def resources_upload_finalize(uploadId: str, total: int, filename: str):
    d=CHUNK_DIR/uploadId
    if not d.is_dir(): raise HTTPException(404,"Upload session không tồn tại.")
    try:
        safe=Path(filename).name
        if not safe.lower().endswith('.zip'): raise HTTPException(400,'Chỉ nhận Resources .zip')
        assembled=UPLOADS/f"assembled_{uploadId}.zip"
        with assembled.open('wb') as out:
            for i in range(int(total)):
                part=d/f"{i:08d}.part"
                if not part.is_file(): raise HTTPException(400,f"Thiếu phần {i+1}/{total}")
                with part.open('rb') as f: shutil.copyfileobj(f,out,1024*1024)
        # Validate and detect/install using the existing manager.
        cp=subprocess.run([sys.executable,str(AUTOMOD/'resource_manager.py'),'--resources',str(RESOURCES),'install',str(assembled)],cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
        if cp.returncode!=0: raise HTTPException(400,cp.stderr or cp.stdout or 'Không thể cài Resources')
        m=re.search(r'Installed Resources version:\s*(.+)',cp.stdout)
        version=m.group(1).strip() if m else ''
        if not version: raise HTTPException(400,'Không xác định được version Resources')
        asset=github_upload_asset(version,assembled)
        manifest=load_resource_manifest(); manifest.setdefault('versions',{})[version]={"version":version,"assetUrl":asset.get('url',''),"browserDownloadUrl":asset.get('browser_download_url',''),"releaseId":asset.get('id'),'uploadedAt':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),"size":assembled.stat().st_size}
        manifest['active']=version; save_resource_manifest(manifest); save_json(ACTIVE,{"version":version,"installedAt":__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()})
        return {"ok":True,"version":version,"stored":True,"size":assembled.stat().st_size}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500,f'Cập nhật Resources thất bại: {e}')
    finally:
        shutil.rmtree(d,ignore_errors=True); assembled.unlink(missing_ok=True)

@app.post("/api/resources/upload")
async def upload_resources_legacy(file: UploadFile = File(...)):
    raise HTTPException(400, "Hãy dùng giao diện upload Resources mới (chunked upload).")

@app.post("/api/scan")
def scan_catalog():
    try:
        restored_version = ensure_local_resources_from_cloud()
    except Exception as e:
        raise HTTPException(409, str(e))
    version_dir = find_latest_version(RESOURCES)
    auto_data = scan(RESOURCES, keep_unresolved=False)
    # Build hero discovery from Garena once, only when admin presses Scan.
    try:
        main_html = fetch_with_fallback(GARNA_MAIN)
        heroes = extract_hero_links(main_html)
        # Filter Auto metadata to heroes that are actually listed by the official Garena hero catalog.
        garena_names = {norm(h.get('heroName', '')) for h in heroes}
        auto_data['heroes'] = [h for h in auto_data.get('heroes', []) if norm(h.get('heroName', '')) in garena_names]
        auto_data['records'] = [r for r in auto_data.get('records', []) if norm(r.get('heroName', '')) in garena_names]
        enriched = []
        def one(h):
            try:
                hi, skins = extract_hero_page(absurl(GARNA_MAIN, f"/hoc-vien/tuong-skin/d/{h['slug']}/"), h["heroName"])
                item = dict(h)
                item["heroImage"] = item.get("heroImage") or hi
                item["_skins"] = skins
                return item
            except Exception as e:
                item = dict(h)
                item["_skins"] = []
                item["scanError"] = str(e)
                return item
        # Scan pages concurrently only when Admin explicitly requests it; normal visitors never do this.
        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = [ex.submit(one, h) for h in heroes]
            for fut in as_completed(futures):
                enriched.append(fut.result())
        enriched.sort(key=lambda x: norm(x.get('heroName','')))
        catalog_data = merge_catalog(auto_data, enriched)
        catalog_data = merge_manual_skins(catalog_data, load_json(CATALOG, {}))
    except Exception as e:
        # Still save Auto-only catalog so admin can see ID/name support even if Garena is temporarily unavailable.
        safe_auto = filter_auto_catalog(auto_data)
        catalog_data = {
            "schemaVersion": 3,
            "resourcesVersion": safe_auto.get("resourcesVersion", version_dir.name),
            "generatedAt": safe_auto.get("generatedAt", ""),
            "heroCount": len(safe_auto.get("heroes", [])),
            "skinCount": sum(len(h.get("skins", [])) for h in safe_auto.get("heroes", [])),
            "garenaScanError": str(e),
            "heroes": [
                {**h, "heroImage": "", "garenaSlug": "", "skins": [
                    {**s, "skinImage": ""} for s in h.get("skins", [])
                ]} for h in safe_auto.get("heroes", [])
            ],
        }
    catalog_data = merge_manual_skins(catalog_data, load_json(CATALOG, {}))
    cloud_warning = _save_catalog_and_persist(catalog_data)
    save_json(ACTIVE, {"version": version_dir.name, "scannedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
    return {"ok": True, "cloudWarning": cloud_warning, **catalog_data}


SCAN_LOCK = threading.Lock()
SCAN_STATE: dict[str, Any] = {"running": False, "progress": "", "error": "", "done": False, "result": None}


def _set_scan_state(**kw):
    with SCAN_LOCK:
        SCAN_STATE.update(kw)


def _run_scan_job():
    """Chạy toàn bộ logic quét Garena + Resources trong 1 luồng nền,
    để request HTTP ban đầu trả lời ngay lập tức và không bị Render/trình
    duyệt cắt kết nối giữa chừng khi quét lâu."""
    _set_scan_state(running=True, progress="Đang kiểm tra Resources...", error="", done=False, result=None)
    try:
        ensure_local_resources_from_cloud()
        version_dir = find_latest_version(RESOURCES)
    except Exception as e:
        _set_scan_state(running=False, done=True, error=str(e))
        return

    _set_scan_state(progress="Đang đọc dữ liệu Resources (AutoMod)...")
    try:
        auto_data = scan(RESOURCES, keep_unresolved=False)
    except Exception as e:
        _set_scan_state(running=False, done=True, error=f"Lỗi đọc Resources: {e}")
        return

    try:
        _set_scan_state(progress="Đang tải danh sách tướng từ Garena...")
        main_html = fetch_with_fallback(GARNA_MAIN)
        heroes = extract_hero_links(main_html)
        garena_names = {norm(h.get('heroName', '')) for h in heroes}
        auto_data['heroes'] = [h for h in auto_data.get('heroes', []) if norm(h.get('heroName', '')) in garena_names]
        auto_data['records'] = [r for r in auto_data.get('records', []) if norm(r.get('heroName', '')) in garena_names]
        enriched: list[dict[str, Any]] = []
        total = len(heroes)
        counter = {"n": 0}

        def one(h):
            try:
                hi, skins = extract_hero_page(absurl(GARNA_MAIN, f"/hoc-vien/tuong-skin/d/{h['slug']}/"), h["heroName"])
                item = dict(h)
                item["heroImage"] = item.get("heroImage") or hi
                item["_skins"] = skins
                return item
            except Exception as e:
                item = dict(h)
                item["_skins"] = []
                item["scanError"] = str(e)
                return item
            finally:
                counter["n"] += 1
                _set_scan_state(progress=f"Đang quét skin từng tướng... ({counter['n']}/{total})")

        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = [ex.submit(one, h) for h in heroes]
            for fut in as_completed(futures):
                enriched.append(fut.result())
        enriched.sort(key=lambda x: norm(x.get('heroName', '')))
        catalog_data = merge_catalog(auto_data, enriched)
    except Exception as e:
        safe_auto = filter_auto_catalog(auto_data)
        catalog_data = {
            "schemaVersion": 3,
            "resourcesVersion": safe_auto.get("resourcesVersion", version_dir.name),
            "generatedAt": safe_auto.get("generatedAt", ""),
            "heroCount": len(safe_auto.get("heroes", [])),
            "skinCount": sum(len(h.get("skins", [])) for h in safe_auto.get("heroes", [])),
            "garenaScanError": str(e),
            "heroes": [
                {**h, "heroImage": "", "garenaSlug": "", "skins": [
                    {**s, "skinImage": ""} for s in h.get("skins", [])
                ]} for h in safe_auto.get("heroes", [])
            ],
        }

    _set_scan_state(progress="Đang lưu catalog...")
    cloud_warning = _save_catalog_and_persist(catalog_data)
    save_json(ACTIVE, {"version": version_dir.name, "scannedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
    _set_scan_state(running=False, done=True, progress=(cloud_warning or "Hoàn tất"), error="", result=catalog_data)


@app.post("/api/scan/start")
def scan_start():
    with SCAN_LOCK:
        if SCAN_STATE.get("running"):
            return {"ok": True, "alreadyRunning": True}
    t = threading.Thread(target=_run_scan_job, daemon=True)
    t.start()
    return {"ok": True, "started": True}


@app.get("/api/scan/status")
def scan_status():
    with SCAN_LOCK:
        state = dict(SCAN_STATE)
    result = state.pop("result", None)
    out = {"ok": True, **state}
    if state.get("done") and not state.get("error") and result:
        out.update(result)
    return out


@app.post("/api/check")
def check_ids(payload: dict[str, Any]):
    ids = [str(x) for x in payload.get("ids", [])]
    data = load_json(CATALOG, {})
    idx = {str(s.get("skinId")): s for h in data.get("heroes", []) for s in h.get("skins", [])}
    return {"resourcesVersion": data.get("resourcesVersion", ""), "results": [
        {"skinId": sid, "found": sid in idx, **(idx.get(sid, {}))} for sid in ids
    ]}


PREMOD_LOCK = threading.Lock()
PREMOD_STATE: dict[str, Any] = {"running": False, "done": False, "progress": "", "total": 0, "doneCount": 0, "okCount": 0, "failCount": 0, "stopRequested": False}


def _set_premod_state(**kw):
    with PREMOD_LOCK:
        PREMOD_STATE.update(kw)


def _run_premod_job():
    """Build sẵn (và lưu cache) toàn bộ skin đang được Resources hỗ trợ, để người
    dùng bình thường bấm 'Tạo & tải ZIP' là có file ngay, không phải chờ build."""
    data = load_json(CATALOG, {})
    if not data and (cloudinary_ready() or github_ready()):
        data = restore_catalog_from_cloud()
    data = sanitize_catalog(data)
    version = data.get("resourcesVersion") or load_json(ACTIVE, {}).get("version", "")
    all_skins = [(h, s) for h in data.get("heroes", []) for s in h.get("skins", []) if s.get("supported")]
    total = len(all_skins)
    _set_premod_state(running=True, done=False, total=total, doneCount=0, okCount=0, failCount=0, progress="Đang chuẩn bị...", stopRequested=False)
    ok = 0
    fail = 0
    for i, (hero, skin) in enumerate(all_skins, start=1):
        with PREMOD_LOCK:
            if PREMOD_STATE.get("stopRequested"):
                break
        skin_id = str(skin.get("skinId"))
        display_name = f"{hero.get('heroName','').strip()} {skin.get('skinName','').strip()}".strip() or skin_id
        display_name = re.sub(r'[\\/:*?"<>|]', '', display_name).strip() or skin_id
        cached = BUILDS / f"{skin_id}_{version}.zip"
        _set_premod_state(progress=f"Đang mod: {display_name} ({i}/{total})")
        try:
            if not (cached.is_file() and cached.stat().st_size > 0):
                built_path, built_version = run_build(skin_id, version, display_name)
                cached = built_path
            # Keep generated AutoMod output outside the ephemeral server disk when Cloudinary is available.
            try:
                persist_build_to_cloud(cached, skin_id, version)
            except Exception as e:
                print(f"[PREMOD] cloud backup failed for {skin_id}: {e}")
            ok += 1
        except Exception:
            fail += 1
        _set_premod_state(doneCount=i, okCount=ok, failCount=fail)
    stopped = PREMOD_STATE.get("stopRequested")
    _set_premod_state(running=False, done=True, progress=("Đã dừng." if stopped else f"Hoàn tất: {ok} thành công, {fail} lỗi."))


def _save_catalog_and_persist(data: dict[str, Any]) -> str:
    data = sanitize_catalog(data)
    save_json(CATALOG, data)
    try:
        return persist_catalog_to_cloud(data) or ""
    except Exception as e:
        return f"Đã lưu cục bộ nhưng backup catalog thất bại: {e}"


@app.post("/api/catalog/hero/{hero_id}/delete")
def delete_hero(hero_id: str):
    data = load_json(CATALOG, {})
    heroes = data.get("heroes", [])
    before = len(heroes)
    heroes = [h for h in heroes if str(h.get("heroId")) != str(hero_id)]
    if len(heroes) == before:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    data["heroes"] = heroes
    data["heroCount"] = len(heroes)
    data["skinCount"] = sum(len(h.get("skins", [])) for h in heroes)
    warn = _save_catalog_and_persist(data)
    return {"ok": True, "cloudWarning": warn, **data}


@app.post("/api/catalog/hero/{hero_id}/skin/{skin_id}/delete")
def delete_skin(hero_id: str, skin_id: str):
    data = load_json(CATALOG, {})
    hero = next((h for h in data.get("heroes", []) if str(h.get("heroId")) == str(hero_id)), None)
    if not hero:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    before = len(hero.get("skins", []))
    hero["skins"] = [s for s in hero.get("skins", []) if str(s.get("skinId")) != str(skin_id)]
    if len(hero["skins"]) == before:
        raise HTTPException(404, "Không tìm thấy skin trong tướng này.")
    hero["skinCount"] = len(hero["skins"])
    data["skinCount"] = sum(len(h.get("skins", [])) for h in data.get("heroes", []))
    warn = _save_catalog_and_persist(data)
    return {"ok": True, "cloudWarning": warn, **data}


class BulkDeletePayload(BaseModel):
    ids: list[str] = []


@app.post("/api/catalog/heroes/delete-many")
def delete_heroes_many(payload: BulkDeletePayload):
    wanted = {str(x) for x in payload.ids if str(x).strip()}
    if not wanted:
        return {"ok": True, "deleted": 0, **load_json(CATALOG, {})}
    data = load_json(CATALOG, {})
    before = len(data.get("heroes", []))
    data["heroes"] = [h for h in data.get("heroes", []) if str(h.get("heroId")) not in wanted]
    deleted = before - len(data["heroes"])
    if deleted:
        data["heroCount"] = len(data["heroes"])
        data["skinCount"] = sum(len(h.get("skins", [])) for h in data["heroes"])
        warn = _save_catalog_and_persist(data)
    else:
        warn = ""
    return {"ok": True, "deleted": deleted, "cloudWarning": warn, **data}


@app.post("/api/catalog/hero/{hero_id}/skins/delete-many")
def delete_skins_many(hero_id: str, payload: BulkDeletePayload):
    wanted = {str(x) for x in payload.ids if str(x).strip()}
    data = load_json(CATALOG, {})
    hero = next((h for h in data.get("heroes", []) if str(h.get("heroId")) == str(hero_id)), None)
    if not hero:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    before = len(hero.get("skins", []))
    hero["skins"] = [s for s in hero.get("skins", []) if str(s.get("skinId")) not in wanted]
    deleted = before - len(hero["skins"])
    hero["skinCount"] = len(hero["skins"])
    data["skinCount"] = sum(len(h.get("skins", [])) for h in data.get("heroes", []))
    warn = _save_catalog_and_persist(data) if deleted else ""
    return {"ok": True, "deleted": deleted, "cloudWarning": warn, **data}


class AddSkinPayload(BaseModel):
    skinName: str
    skinId: str
    imageUrl: str


@app.post("/api/catalog/hero/{hero_id}/skin/add")
def add_skin(hero_id: str, payload: AddSkinPayload):
    data = load_json(CATALOG, {})
    hero = next((h for h in data.get("heroes", []) if str(h.get("heroId")) == str(hero_id)), None)
    if not hero:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    sid = str(payload.skinId or "").strip()
    name = str(payload.skinName or "").strip()
    image = str(payload.imageUrl or "").strip()
    if not re.fullmatch(r"\d{5}", sid):
        raise HTTPException(400, "ID skin phải đúng 5 chữ số, ví dụ 59903.")
    if not name:
        raise HTTPException(400, "Vui lòng nhập tên skin.")
    if not image:
        raise HTTPException(400, "Vui lòng nhập URL ảnh hoặc tải ảnh từ máy.")
    if is_hidden_skin_name(name):
        raise HTTPException(400, "Tên skin dạng [EX]/Mặc định không được thêm vào catalog Auto Mod.")
    if any(str(s.get("skinId")) == sid for s in hero.get("skins", [])):
        raise HTTPException(409, f"Skin ID {sid} đã tồn tại trong tướng này.")
    version = data.get("resourcesVersion") or load_json(ACTIVE, {}).get("version", "")
    hero.setdefault("skins", []).append({
        "skinId": sid,
        "skinName": name,
        "skinImage": image,
        "resolved": True,
        "supported": True,
        "manualAdded": True,
        "resourcesVersion": version,
        "imageMissing": False,
    })
    hero["skinCount"] = len(hero.get("skins", []))
    data["skinCount"] = sum(len(h.get("skins", [])) for h in data.get("heroes", []))
    warn = _save_catalog_and_persist(data)
    return {"ok": True, "cloudWarning": warn, **data}


class ImageEditPayload(BaseModel):
    imageUrl: str


@app.post("/api/catalog/hero/{hero_id}/image")
def set_hero_image(hero_id: str, payload: ImageEditPayload):
    data = load_json(CATALOG, {})
    hero = next((h for h in data.get("heroes", []) if str(h.get("heroId")) == str(hero_id)), None)
    if not hero:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    hero["heroImage"] = payload.imageUrl.strip()
    warn = _save_catalog_and_persist(data)
    return {"ok": True, "cloudWarning": warn, **data}


@app.post("/api/catalog/hero/{hero_id}/skin/{skin_id}/image")
def set_skin_image(hero_id: str, skin_id: str, payload: ImageEditPayload):
    data = load_json(CATALOG, {})
    hero = next((h for h in data.get("heroes", []) if str(h.get("heroId")) == str(hero_id)), None)
    if not hero:
        raise HTTPException(404, "Không tìm thấy tướng trong catalog.")
    skin = next((s for s in hero.get("skins", []) if str(s.get("skinId")) == str(skin_id)), None)
    if not skin:
        raise HTTPException(404, "Không tìm thấy skin trong tướng này.")
    skin["skinImage"] = payload.imageUrl.strip()
    skin["imageMissing"] = not bool(skin["skinImage"])
    warn = _save_catalog_and_persist(data)
    return {"ok": True, "cloudWarning": warn, **data}


@app.post("/api/premod/start")
def premod_start():
    with PREMOD_LOCK:
        if PREMOD_STATE.get("running"):
            return {"ok": True, "alreadyRunning": True}
    t = threading.Thread(target=_run_premod_job, daemon=True)
    t.start()
    return {"ok": True, "started": True}


@app.post("/api/premod/stop")
def premod_stop():
    _set_premod_state(stopRequested=True)
    return {"ok": True}


@app.get("/api/premod/status")
def premod_status():
    with PREMOD_LOCK:
        return {"ok": True, **PREMOD_STATE}


@app.post("/api/build/{skin_id}")
def build_skin(skin_id: str):
    data = load_json(CATALOG, {})
    if not data and (cloudinary_ready() or github_ready()):
        data = restore_catalog_from_cloud()
    data = sanitize_catalog(data)
    try:
        ensure_local_resources_from_cloud(data.get("resourcesVersion") or None)
    except Exception as e:
        raise HTTPException(409, str(e))
    skins = {str(s.get("skinId")): (h, s) for h in data.get("heroes", []) for s in h.get("skins", [])}
    if skin_id not in skins:
        raise HTTPException(404, "Skin ID chưa có trong catalog.")
    hero, skin = skins[skin_id]
    version = data.get("resourcesVersion") or load_json(ACTIVE, {}).get("version", "")
    if not skin.get("supported", False):
        raise HTTPException(409, f"Skin chưa được Resources {version or 'hiện tại'} hỗ trợ.")
    # Tên tướng + tên skin thật (vd "Billow Okarun"), dùng làm tên gói bên trong ZIP
    # và tên file tải về, thay vì chỉ dùng số Skin ID trần trụi.
    display_name = f"{hero.get('heroName','').strip()} {skin.get('skinName','').strip()}".strip() or skin_id
    display_name = re.sub(r'[\\/:*?"<>|]', '', display_name).strip() or skin_id
    cached = BUILDS / f"{skin_id}_{version}.zip"
    if not (cached.is_file() and cached.stat().st_size > 0):
        restored = restore_build_from_cloud(skin_id, version)
        if restored:
            cached = restored
    if cached.is_file() and cached.stat().st_size > 0:
        out = cached
    else:
        try:
            out, version = run_build(skin_id, version, display_name)
            try:
                persist_build_to_cloud(out, skin_id, version)
            except Exception as e:
                print(f"[BUILD] cloud backup failed for {skin_id}: {e}")
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Build mod quá lâu, đã dừng.")
        except Exception as e:
            raise HTTPException(500, f"Build mod thất bại: {e}")
    # Trả thẳng file ZIP ngay trong response này (không bắt trình duyệt gọi thêm
    # 1 request /download riêng), để tránh trường hợp request tải sau đó bị lệch
    # sang một instance/tiến trình khác (hoặc ổ đĩa tạm đã dọn) không còn thấy file.
    if not out.is_file():
        raise HTTPException(500, "Build xong nhưng không tìm thấy file ZIP để trả về.")
    return FileResponse(str(out), filename=f"{display_name}.zip", media_type="application/zip")


app.mount("/", StaticFiles(directory=str(ROOT / "web"), html=True), name="web")

@app.get("/download/{name}")
def download(name: str):
    p = (BUILDS / Path(name).name).resolve()
    if not p.is_file() or not str(p).startswith(str(BUILDS.resolve())):
        raise HTTPException(404, "Không tìm thấy file.")
    return FileResponse(str(p), filename=p.name)

