#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

LANG_FILES = [
    'languageMap.txt',
    'languageMap_Newbie.txt',
    'languageMap_WorldConcept.txt',
    'languageMap_Xls.txt',
    'lanMapIncremental.txt',
]


def version_key(name: str):
    parts = re.findall(r'\d+|[A-Za-z]+', name)
    return [(0, int(p)) if p.isdigit() else (1, p.lower()) for p in parts]


def find_resource_versions(root: Path) -> List[Path]:
    out = []
    if not root.is_dir():
        return out
    for p in root.iterdir():
        if not p.is_dir() or not re.search(r'\d', p.name):
            continue
        hero = p / 'Databin' / 'Client' / 'Actor' / 'heroSkin.bytes'
        lang = p / 'Languages' / 'VN_Garena_VN'
        if hero.is_file() and lang.is_dir():
            out.append(p)
    return sorted(out, key=lambda p: version_key(p.name))


def find_latest_version(root: Path) -> Path:
    versions = find_resource_versions(root)
    if not versions:
        raise FileNotFoundError(f'No valid Resources/<version> found under {root}')
    return versions[-1]


def decompress_custom_blob(data: bytes, zstd_dict: Path) -> bytes:
    # AutoMod's format: 4-byte marker + 4-byte raw-size + zstd frame.
    if data.startswith(b'\x22\x4a\x00\xef') and data.find(b'\x28\xb5\x2f\xfd') == 8:
        frame = data[8:]
    elif data.find(b'\x28\xb5\x2f\xfd') >= 0:
        frame = data[data.find(b'\x28\xb5\x2f\xfd'):]
    else:
        return data

    try:
        import pyzstd  # type: ignore
        return pyzstd.decompress(frame, pyzstd.ZstdDict(zstd_dict.read_bytes(), is_raw=True))
    except ImportError:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / 'in.zst'
            dst = td / 'out.bin'
            src.write_bytes(frame)
            cp = subprocess.run(
                ['zstd', '-d', '-q', '-D', str(zstd_dict), '-f', str(src), '-o', str(dst)],
                capture_output=True, text=True
            )
            if cp.returncode != 0:
                raise RuntimeError(f'Cannot decompress zstd blob: {cp.stderr.strip()}')
            return dst.read_bytes()


def load_data_file(path: Path, zstd_dict: Path) -> bytes:
    return decompress_custom_blob(path.read_bytes(), zstd_dict)


def build_language_index(map_bytes: bytes) -> Dict[bytes, str]:
    # Mirrors AutoMod's lookup logic: find a 19-byte key, then take text
    # after the 22-byte entry prefix until CR/LF.
    idx: Dict[bytes, str] = {}
    start = 0
    n = len(map_bytes)
    while start < n:
        nl = map_bytes.find(b'\n', start)
        if nl < 0:
            nl = n
        line = map_bytes[start:nl].rstrip(b'\r')
        if len(line) >= 23:
            # Keys used by AutoMod are 19 bytes immediately before the value prefix.
            # We index several plausible 19-byte windows to tolerate map variants.
            for off in range(min(22, max(0, len(line) - 19)) + 1):
                key = line[off:off + 19]
                if len(key) == 19:
                    val = line[22:]
                    if val:
                        try:
                            text = val.decode('utf-8', 'ignore').strip('\x00\r\n')
                        except Exception:
                            continue
                        if text:
                            idx.setdefault(key, text)
        start = nl + 1
    return idx


def lookup_key(map_bytes: bytes, key: bytes) -> Optional[str]:
    pos = map_bytes.find(key)
    if pos < 0:
        return None
    end = map_bytes.find(b'\r', pos)
    if end < 0:
        end = map_bytes.find(b'\n', pos)
    if end < 0:
        end = len(map_bytes)
    if end < pos + 22:
        return None
    return map_bytes[pos + 22:end].decode('utf-8', 'ignore').strip('\x00\r\n') or None


def iter_skin_records(hero_skin: bytes) -> Iterable[Tuple[int, int, int]]:
    seen = set()
    # Record marker used by AutoMod: skin_id LE32 + hero_id LE32.
    for pos in range(0, len(hero_skin) - 7):
        skin_id, hero_id = struct.unpack_from('<II', hero_skin, pos)
        if not (10000 <= skin_id <= 99999):
            continue
        if skin_id // 100 != hero_id:
            continue
        if not (100 <= hero_id <= 999):
            continue
        item = (skin_id, hero_id, pos)
        key = (skin_id, hero_id)
        if key not in seen:
            seen.add(key)
            yield item


def scan(resources_root: Path, keep_unresolved: bool = False, id_allowlist: Optional[set[str]] = None) -> dict:
    version_dir = find_latest_version(resources_root)
    base = version_dir
    zstd_dict = resources_root.parent / 'automod' / 'FILES_CODE' / 'ZSTD_DICT.xml'
    # If the dictionary isn't beside the Resources directory, fall back to the
    # dictionary bundled next to this script.
    if not zstd_dict.is_file():
        zstd_dict = Path(__file__).with_name('ZSTD_DICT.xml')
    if not zstd_dict.is_file():
        raise FileNotFoundError('ZSTD_DICT.xml is required for compressed Resources')

    hero_path = base / 'Databin' / 'Client' / 'Actor' / 'heroSkin.bytes'
    hero = load_data_file(hero_path, zstd_dict)
    maps = []
    for name in LANG_FILES:
        p = base / 'Languages' / 'VN_Garena_VN' / name
        if p.is_file():
            maps.append((name, load_data_file(p, zstd_dict)))

    records = []
    for skin_id, hero_id, pos in iter_skin_records(hero):
        hero_key = hero[pos + 12:pos + 31]
        skin_key = hero[pos + 40:pos + 59]
        hero_name = None
        skin_name = None
        source_map = None
        for map_name, mb in maps:
            h = lookup_key(mb, hero_key)
            s = lookup_key(mb, skin_key)
            if h and s:
                hero_name, skin_name, source_map = h, s, map_name
                break
        item = {
            'skinId': str(skin_id),
            'heroId': str(hero_id),
            'heroName': hero_name or '',
            'skinName': skin_name or '',
            'resolved': bool(hero_name and skin_name),
            'resourcesVersion': version_dir.name,
            'sourceMap': source_map or '',
        }
        if item['resolved'] and (id_allowlist is None or item['skinId'] in id_allowlist):
            records.append(item)
        elif keep_unresolved and (id_allowlist is None or item['skinId'] in id_allowlist):
            records.append(item)

    # Group by hero while preserving numeric ordering.
    heroes: Dict[str, dict] = {}
    for r in sorted(records, key=lambda x: int(x['skinId'])):
        h = heroes.setdefault(r['heroId'], {
            'heroId': r['heroId'],
            'heroName': r['heroName'],
            'skins': []
        })
        h['skins'].append({
            'skinId': r['skinId'],
            'skinName': r['skinName'],
            'resolved': r['resolved'],
            'resourcesVersion': r['resourcesVersion'],
        })

    return {
        'schemaVersion': 1,
        'resourcesVersion': version_dir.name,
        'generatedAt': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'recordCount': len(records),
        'resolvedCount': sum(1 for r in records if r['resolved']),
        'heroes': list(sorted(heroes.values(), key=lambda h: int(h['heroId']))),
        'records': records,
    }


def main():
    ap = argparse.ArgumentParser(description='NGOCC / AutoMod skin metadata scanner')
    ap.add_argument('--resources', default='Resources', help='Resources folder containing version folders')
    ap.add_argument('--out', default='skin_catalog.json')
    ap.add_argument('--include-unresolved', action='store_true')
    ap.add_argument('--id-list', help='Text file containing skin IDs to restrict output to')
    args = ap.parse_args()
    allow=None
    if args.id_list:
        txt=Path(args.id_list).read_text(encoding='utf-8',errors='ignore')
        allow=set(re.findall(r'(?<!\d)\d{5}(?!\d)',txt))
    data = scan(Path(args.resources), args.include_unresolved, allow)
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Resources version: {data['resourcesVersion']}")
    print(f"Heroes: {len(data['heroes'])}")
    print(f"Records: {data['recordCount']}")
    print(f"Resolved names: {data['resolvedCount']}")
    print(f"Output: {args.out}")

if __name__ == '__main__':
    main()
