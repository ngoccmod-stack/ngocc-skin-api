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
import unicodedata
import zipfile
import uuid
from pathlib import Path
from typing import Any

import requests
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from bs4 import BeautifulSoup
from fastapi import FastAPI, File, HTTPException, UploadFile
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
CLOUDINARY_FOLDER = os.environ.get("NGOCC_CLOUDINARY_FOLDER", "ngocc_resources").strip("/")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "ngoccmod-stack/ngocc-skin-api").strip()
CHUNK_DIR = UPLOADS / "resource_chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

for p in (RESOURCES, DATA, UPLOADS, BUILDS):
    p.mkdir(parents=True, exist_ok=True)

if os.environ.get("CLOUDINARY_URL"):
    cloudinary.config(secure=True)

sys.path.insert(0, str(AUTOMOD))
from skin_catalog_scanner import find_latest_version, scan  # noqa: E402
from build_runner import build_skin as run_build  # noqa: E402

app = FastAPI(title="NGOCC Skin System API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

GARNA_MAIN = "https://lienquan.garena.vn/hoc-vien/tuong-skin/"
HEADERS = {"User-Agent": "Mozilla/5.0 (NGOCC Skin Scanner)"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
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
    # Garena pages expose skin names as headings and the corresponding image in nearby markup.
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = " ".join(heading.stripped_strings).strip()
        if not text or not norm(text).startswith(norm(hero_name)):
            continue
        skin_name = re.sub(rf"^{re.escape(hero_name)}\s*", "", text, flags=re.I).strip()
        if not skin_name or norm(skin_name) in {"trang phuc", "ky nang"}:
            continue
        img = heading.find_next("img")
        src = absurl(hero_url, img.get("src") if img else "")
        if src:
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


def merge_catalog(auto_data: dict[str, Any], garena_heroes: list[dict[str, str]]) -> dict[str, Any]:
    by_name = {norm(h.get("heroName", "")): h for h in garena_heroes}
    # If duplicate/current naming differs, also index by slug.
    result = {
        "schemaVersion": 2,
        "resourcesVersion": auto_data.get("resourcesVersion", ""),
        "generatedAt": auto_data.get("generatedAt", ""),
        "heroCount": 0,
        "skinCount": 0,
        "heroes": [],
    }
    for h in auto_data.get("heroes", []):
        hero_id = str(h.get("heroId", ""))
        hero_name = h.get("heroName", "")
        g = by_name.get(norm(hero_name), {})
        # Some Garena pages include duplicate Flowborn entries; keep whichever image exists.
        hero = {
            "heroId": hero_id,
            "heroName": hero_name,
            "heroImage": g.get("heroImage", ""),
            "garenaSlug": g.get("slug", ""),
            "skins": [],
        }
        for s in h.get("skins", []):
            hero["skins"].append({
                "skinId": str(s.get("skinId", "")),
                "skinName": s.get("skinName", ""),
                "skinImage": "",
                "supported": bool(s.get("resolved")),
                "resourcesVersion": s.get("resourcesVersion", result["resourcesVersion"]),
            })
        result["heroes"].append(hero)

    # Match skin images by normalized source name, then by page order as a safe fallback.
    for hero in result["heroes"]:
        garena = next((x for x in garena_heroes if x.get("slug") == hero.get("garenaSlug")), None)
        if not garena or not garena.get("_skins"):
            continue
        source_skins = garena["_skins"]
        by_skin_name = {norm(x["skinNameSource"]): x["skinImage"] for x in source_skins}
        used = set()
        for idx, s in enumerate(hero["skins"]):
            key = norm(s["skinName"])
            img = by_skin_name.get(key, "")
            if not img and idx < len(source_skins):
                # Order is the fallback because Garena renders skins in the same sequence used by the page.
                img = source_skins[idx].get("skinImage", "")
            s["skinImage"] = img
            if img:
                used.add(img)
            if not s["skinImage"]:
                s["imageMissing"] = True
        hero["skinCount"] = len(hero["skins"])
    result["heroCount"] = len(result["heroes"])
    result["skinCount"] = sum(len(h["skins"]) for h in result["heroes"])
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
    if not cloudinary_ready():
        return ""
    local = DATA / "skin_catalog.json"
    local.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    result = cloudinary.uploader.upload(
        str(local), resource_type="raw", public_id=catalog_public_id(), overwrite=True
    )
    return result.get("secure_url") or catalog_secure_url()


def restore_catalog_from_cloud() -> dict[str, Any]:
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
    if not target: raise FileNotFoundError('Chưa có Resources; Admin hãy cập nhật Resources trước.')
    info=manifest.get('versions',{}).get(target) or {}
    asset_url=info.get('assetUrl')
    if not asset_url:
        # Try resolving from release tag.
        if not GITHUB_TOKEN: raise FileNotFoundError('Chưa có GITHUB_TOKEN để khôi phục Resources.')
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


@app.get("/api/catalog")
def catalog():
    data = load_json(CATALOG, {})
    if not data and cloudinary_ready():
        data = restore_catalog_from_cloud()
    if not data:
        return JSONResponse({"ready": False, "heroes": [], "skinCount": 0})
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
    except Exception as e:
        # Still save Auto-only catalog so admin can see ID/name support even if Garena is temporarily unavailable.
        catalog_data = {
            "schemaVersion": 2,
            "resourcesVersion": auto_data.get("resourcesVersion", version_dir.name),
            "generatedAt": auto_data.get("generatedAt", ""),
            "heroCount": len(auto_data.get("heroes", [])),
            "skinCount": sum(len(h.get("skins", [])) for h in auto_data.get("heroes", [])),
            "garenaScanError": str(e),
            "heroes": [
                {**h, "heroImage": "", "garenaSlug": "", "skins": [
                    {**s, "skinImage": ""} for s in h.get("skins", [])
                ]} for h in auto_data.get("heroes", [])
            ],
        }
    save_json(CATALOG, catalog_data)
    try:
        persist_catalog_to_cloud(catalog_data)
    except Exception:
        pass
    save_json(ACTIVE, {"version": version_dir.name, "scannedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
    return {"ok": True, **catalog_data}


@app.post("/api/check")
def check_ids(payload: dict[str, Any]):
    ids = [str(x) for x in payload.get("ids", [])]
    data = load_json(CATALOG, {})
    idx = {str(s.get("skinId")): s for h in data.get("heroes", []) for s in h.get("skins", [])}
    return {"resourcesVersion": data.get("resourcesVersion", ""), "results": [
        {"skinId": sid, "found": sid in idx, **(idx.get(sid, {}))} for sid in ids
    ]}


@app.post("/api/build/{skin_id}")
def build_skin(skin_id: str):
    data = load_json(CATALOG, {})
    if not data and cloudinary_ready():
        data = restore_catalog_from_cloud()
    try:
        ensure_local_resources_from_cloud(data.get("resourcesVersion") or None)
    except Exception as e:
        raise HTTPException(409, str(e))
    skins = {str(s.get("skinId")): (h, s) for h in data.get("heroes", []) for s in h.get("skins", [])}
    if skin_id not in skins:
        raise HTTPException(404, "Skin ID chưa có trong catalog.")
    version = data.get("resourcesVersion") or load_json(ACTIVE, {}).get("version", "")
    if not skins[skin_id][1].get("supported", False):
        raise HTTPException(409, f"Skin chưa được Resources {version or 'hiện tại'} hỗ trợ.")
    cached = BUILDS / f"{skin_id}_{version}.zip"
    if cached.is_file() and cached.stat().st_size > 0:
        return {"ok": True, "cached": True, "resourcesVersion": version, "downloadUrl": f"/download/{cached.name}"}
    try:
        out, used_version = run_build(skin_id, version)
        return {"ok": True, "cached": False, "resourcesVersion": used_version, "downloadUrl": f"/download/{out.name}"}
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Build mod quá lâu, đã dừng.")
    except Exception as e:
        raise HTTPException(500, f"Build mod thất bại: {e}")


app.mount("/", StaticFiles(directory=str(ROOT / "web"), html=True), name="web")

@app.get("/download/{name}")
def download(name: str):
    p = (BUILDS / Path(name).name).resolve()
    if not p.is_file() or not str(p).startswith(str(BUILDS.resolve())):
        raise HTTPException(404, "Không tìm thấy file.")
    return FileResponse(str(p), filename=p.name)
