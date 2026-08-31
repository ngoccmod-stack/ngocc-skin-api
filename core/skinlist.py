# -*- coding: utf-8 -*-
"""Doc skin.txt + quet Source -> danh sach button mod duoc."""
import os, re, glob

_ID_LINE = re.compile(r'^\s*(\d{4,6})\s*[-\u2013\u2014:]\s*(.+?)\s*$')
_HERO    = re.compile(r'^\s*(\S.*?)\s*:\s*$')


def parse_skin_txt(path):
    out, hero = {}, ''
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = _ID_LINE.match(line)
            if m:
                out[m.group(1)] = (m.group(2), hero); continue
            m = _HERO.match(line)
            if m and not m.group(1)[0].isdigit():
                hero = m.group(1)
    return out


def scan_source(src_dir):
    res = {}
    for p in glob.glob(os.path.join(src_dir, '**', '*.assetbundle'), recursive=True):
        b = os.path.basename(p)
        m = re.match(r'^personalbutton(effect|sprite)_(\d+)(_raw)?\.assetbundle$', b, re.I)
        if not m:
            continue
        kind, sid, raw = m.group(1).lower(), m.group(2), bool(m.group(3))
        d = res.setdefault(sid, {'effect': None, 'effect_raw': None, 'sprite_raw': None})
        if kind == 'effect':
            d['effect_raw' if raw else 'effect'] = p
        elif kind == 'sprite' and raw:
            d['sprite_raw'] = p
    return res


def build_menu(src_dir, skin_txt):
    skins = parse_skin_txt(skin_txt) if os.path.isfile(skin_txt) else {}
    files = scan_source(src_dir)
    # Suy ra ten tuong cho ID moi bang 3 so dau neu skin.txt khong co ID day.
    hero_by_prefix = {}
    for known_id, (known_name, known_hero) in skins.items():
        if known_hero and len(known_id) >= 3:
            hero_by_prefix.setdefault(known_id[:3], known_hero)

    rows = []
    for sid, f in files.items():
        if not (f['effect'] or f['sprite_raw']):
            continue
        if sid in skins:
            name, hero, known = skins[sid][0], skins[sid][1], True
        else:
            hero = hero_by_prefix.get(sid[:3], '') if len(sid) >= 3 else ''
            name, known = ('Skin %s?' % sid, False)
        parts = []
        if f['effect']:    parts.append('FX')
        if f['sprite_raw']: parts.append('JOY')
        rows.append({'id': sid, 'name': name, 'hero': hero,
                     'parts': '+'.join(parts) or '-', 'files': f, 'known': known})
    # ID moi van duoc hien cung nhom tuong, nhung skin co ten that uu tien truoc.
    rows.sort(key=lambda r: (r['hero'].lower(), not r['known'], int(r['id'])))
    return rows
