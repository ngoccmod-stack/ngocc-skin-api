from pathlib import Path
import shutil, sys, py_compile

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
server = root / 'server.py'
if not server.is_file():
    raise SystemExit(f'Khong tim thay {server}')

text = server.read_text(encoding='utf-8')
backup = server.with_suffix('.py.bak-before-skin-fix')
if not backup.exists():
    shutil.copy2(server, backup)

def rep(old, new, label, count=1):
    global text
    if old not in text:
        raise RuntimeError('Khong tim thay: ' + label)
    text = text.replace(old, new, count)

# Keep unresolved Resources records. This prevents missing language-map keys from
# deleting an otherwise valid skin ID before Garena enrichment.
text = text.replace('scan(RESOURCES, keep_unresolved=False)', 'scan(RESOURCES, keep_unresolved=True)')

# Remove the two hard Garena-name allow-list filters.
text = text.replace("""        garena_names = {norm(h.get('heroName', '')) for h in heroes}\n        auto_data['heroes'] = [h for h in auto_data.get('heroes', []) if norm(h.get('heroName', '')) in garena_names]\n        auto_data['records'] = [r for r in auto_data.get('records', []) if norm(r.get('heroName', '')) in garena_names]\n""", '', 2)

# Capture official skin IDs from Garena page anchors. The old scanner only used names.
old = '''    skins: list[dict[str, str]] = []\n    # Ưu tiên lấy ẢNH LỚN nằm ngay dưới tên mỗi skin (ảnh chính giữa trang), theo đúng'''
new = '''    skins: list[dict[str, str]] = []\n\n    def extract_skin_id(href: str) -> str:\n        m = re.search(r"#heroSkin-(\\d{5})", str(href or ""), flags=re.I)\n        return m.group(1) if m else ""\n\n    # Ưu tiên lấy ẢNH LỚN nằm ngay dưới tên mỗi skin (ảnh chính giữa trang), theo đúng'''
rep(old, new, 'skin helper')

old = '''        if src:\n            skins.append({"skinNameSource": skin_name, "skinImage": src})\n    # Nếu không tìm được ảnh theo cách trên (trang đổi cấu trúc), rơi về mục\n    # "Trang phục" (gallery nhỏ) để ít nhất vẫn có ảnh, còn hơn không có.\n    if not skins:\n        outfit_heading = None\n        for h in soup.find_all(["h2", "h3", "h4"]):\n            if norm(" ".join(h.stripped_strings)) == "trang phuc":\n                outfit_heading = h\n                break\n        if outfit_heading is not None:\n            container = outfit_heading.find_next(["ul", "ol", "div"])\n            anchors = container.find_all("a", href=re.compile(r"#heroSkin-\\d+")) if container else []\n            for a in anchors:\n                img = a.find("img")\n                if not img:\n                    continue\n                full_name = (a.get("title") or img.get("alt") or img.get("title") or "").strip()\n                src = absurl(hero_url, img.get("src"))\n                if not full_name or not src:\n                    continue\n                skin_name = re.sub(rf"^{re.escape(hero_name)}\\s*", "", full_name, flags=re.I).strip() or full_name\n                skins.append({"skinNameSource": skin_name, "skinImage": src})\n    # De-duplicate exact names.\n    seen_names = set()'''
new = '''        if src:\n            skin_id = ""\n            for a in heading.find_all_next("a", href=re.compile(r"#heroSkin-\\d+"), limit=8):\n                skin_id = extract_skin_id(a.get("href"))\n                if skin_id:\n                    break\n            skins.append({"skinNameSource": skin_name, "skinImage": src, "skinId": skin_id})\n\n    # Always supplement from the official Trang phục anchors.  Previously this\n    # fallback only ran when zero headings were found, so partially parsed pages\n    # silently lost skins.\n    for a in soup.find_all("a", href=re.compile(r"#heroSkin-\\d+")):\n        img = a.find("img")\n        full_name = (a.get("title") or a.get("aria-label") or\n                     (img.get("alt") if img else "") or\n                     (img.get("title") if img else "") or "").strip()\n        sid = extract_skin_id(a.get("href"))\n        src = absurl(hero_url, img.get("src") if img else "")\n        if not sid or not full_name:\n            continue\n        skin_name = re.sub(rf"^{re.escape(hero_name)}\\s*", "", full_name, flags=re.I).strip() or full_name\n        skins.append({"skinNameSource": skin_name, "skinImage": src, "skinId": sid})\n\n    # De-duplicate by stable skin ID first, then normalized name.\n    seen_ids = set()\n    seen_names = set()'''
rep(old, new, 'skin extraction block')

old = '''    for s in skins:\n        k = norm(s["skinNameSource"])\n        if k and k not in seen_names:\n            seen_names.add(k)\n            uniq.append(s)'''
new = '''    for s in skins:\n        sid = str(s.get("skinId", "")).strip()\n        k = norm(s["skinNameSource"])\n        if sid and sid in seen_ids:\n            continue\n        if sid:\n            seen_ids.add(sid)\n        if k and k not in seen_names:\n            seen_names.add(k)\n            uniq.append(s)'''
rep(old, new, 'skin dedupe')

# Use hero_id from the 5-digit skin ID as a secondary official matching key.
old = '''    by_name = {norm(h.get("heroName", "")): h for h in garena_heroes if is_valid_hero_name(h.get("heroName", ""))}\n    result = {'''
new = '''    by_name = {norm(h.get("heroName", "")): h for h in garena_heroes if is_valid_hero_name(h.get("heroName", ""))}\n    by_hero_id = {}\n    for g in garena_heroes:\n        for s in (g.get("_skins") or []):\n            sid = str(s.get("skinId", "")).strip()\n            if re.fullmatch(r"\\d{5}", sid):\n                by_hero_id.setdefault(sid[:3], g)\n                break\n    result = {'''
rep(old, new, 'hero id lookup')

old = '''        g = by_name.get(norm(hero_name))\n        # When official Garena data is available, accept only heroes actually present there.\n        if not g:\n            continue\n        key = norm(hero_name) or hero_id'''
new = '''        g = by_name.get(norm(hero_name)) or by_hero_id.get(hero_id)\n        # Do not discard a Resources hero only because its localized name differs\n        # from Garena. The numeric hero ID remains stable through the skin ID.\n        key = norm(hero_name) or hero_id'''
rep(old, new, 'hard hero filter in merge_catalog')

old = '''                "heroName": hero_name,\n                "heroImage": g.get("heroImage", ""),\n                "garenaSlug": g.get("slug", ""),'''
new = '''                "heroName": hero_name or (g.get("heroName", "") if g else ""),\n                "heroImage": g.get("heroImage", "") if g else "",\n                "garenaSlug": g.get("slug", "") if g else "",'''
rep(old, new, 'hero fallback fields')

# Match skin images by ID before name. This fixes punctuation/localization changes.
old = '''        source_skins = [x for x in garena["_skins"] if not is_hidden_skin_name(x.get("skinNameSource", ""))]\n        by_skin_name: dict[str, list[dict[str, str]]] = {}'''
new = '''        source_skins = [x for x in garena["_skins"] if not is_hidden_skin_name(x.get("skinNameSource", ""))]\n        by_skin_id = {\n            str(x.get("skinId", "")).strip(): x\n            for x in source_skins\n            if str(x.get("skinId", "")).strip()\n        }\n        by_skin_name: dict[str, list[dict[str, str]]] = {}'''
rep(old, new, 'skin id lookup')

old = '''        for skin in hero["skins"]:\n            key = norm(skin["skinName"])\n            img = ""\n            for c in by_skin_name.get(key, []):'''
new = '''        for skin in hero["skins"]:\n            key = norm(skin["skinName"])\n            sid = str(skin.get("skinId", "")).strip()\n            img = ""\n            by_id = by_skin_id.get(sid)\n            if by_id:\n                if by_id.get("skinNameSource") and not key:\n                    skin["skinName"] = by_id["skinNameSource"]\n                    key = norm(skin["skinName"])\n                img = by_id.get("skinImage", "") or ""\n            for c in by_skin_name.get(key, []):'''
rep(old, new, 'skin id image matching')

server.write_text(text, encoding='utf-8')
py_compile.compile(str(server), doraise=True)
print('OK - da patch server.py')
print('Backup:', backup)
