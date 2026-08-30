#!/usr/bin/env python3
"""Manage versioned AutoMod Resources and skin metadata scans.

Commands:
  list                         list detected Resources versions
  active                       print newest valid Resources version
  check ID [ID ...]            check IDs against active heroSkin.bytes
  scan                         create skin_catalog.json from active Resources
  install ZIP                  install a Resources ZIP under Resources/<version>
"""
from __future__ import annotations
import argparse, re, shutil, zipfile
from pathlib import Path
from skin_catalog_scanner import find_resource_versions, scan


def versions(root: Path):
    return find_resource_versions(root)


def detect_version_from_zip(z: zipfile.ZipFile):
    candidates=[]
    for n in z.namelist():
        m=re.match(r'(?:.*/)?Resources/(\d+(?:\.\d+)+)/Databin/Client/Actor/heroSkin\.bytes$', n)
        if m: candidates.append(m.group(1))
        m2=re.match(r'(?:.*/)?Resources/(\d+(?:\.\d+)+)/.*$', n)
        if m2: candidates.append(m2.group(1))
    if not candidates:
        raise ValueError('Không tìm thấy Resources/<version> trong ZIP.')
    return sorted(set(candidates), key=lambda x: [(0,int(p)) if p.isdigit() else (1,p) for p in re.findall(r'\d+|[A-Za-z]+',x)])[-1]


def install_zip(zip_path: Path, root: Path):
    with zipfile.ZipFile(zip_path) as z:
        version=detect_version_from_zip(z)
        prefix_matches=[n for n in z.namelist() if f'Resources/{version}/' in n]
        if not prefix_matches:
            raise ValueError(f'ZIP không chứa Resources/{version}.')
        tmp=root.parent / (root.name + '_install_tmp')
        shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)
        try:
            for n in prefix_matches:
                rel=n.split(f'Resources/{version}/',1)[1]
                if not rel: continue
                dest=tmp/version/rel
                if n.endswith('/'):
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(n) as src, open(dest,'wb') as dst: shutil.copyfileobj(src,dst)
            target=root/version
            if target.exists(): shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(tmp/version), str(target))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return version


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--resources', default='Resources')
    sp=ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('list')
    sp.add_parser('active')
    c=sp.add_parser('check'); c.add_argument('ids', nargs='+')
    s=sp.add_parser('scan'); s.add_argument('--out', default='skin_catalog.json'); s.add_argument('--include-unresolved', action='store_true')
    i=sp.add_parser('install'); i.add_argument('zipfile')
    args=ap.parse_args(); root=Path(args.resources)
    if args.cmd=='list':
        for p in versions(root): print(p.name)
    elif args.cmd=='active': print(versions(root)[-1].name if versions(root) else 'NONE')
    elif args.cmd=='install': print('Installed Resources version:',install_zip(Path(args.zipfile),root))
    elif args.cmd=='scan':
        data=scan(root,args.include_unresolved); Path(args.out).write_text(__import__('json').dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); print(f"Scanned {data['recordCount']} records from {data['resourcesVersion']} -> {args.out}")
    elif args.cmd=='check':
        data=scan(root, True); idx={r['skinId']:r for r in data['records']}
        for sid in args.ids:
            r=idx.get(str(sid));
            print(f"{sid}: ✅ {r['heroName']} - {r['skinName']} (Resources {data['resourcesVersion']})" if r else f"{sid}: ❌ not found in active Resources {data['resourcesVersion']}")

if __name__=='__main__': main()
