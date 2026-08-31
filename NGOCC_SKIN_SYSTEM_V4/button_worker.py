#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, time, importlib
from pathlib import Path


def emit(kind: str, value: object = ''):
    print(f'@@{kind}@@{value}', flush=True)


def main() -> int:
    if len(sys.argv) != 2:
        emit('ERROR', 'Thiếu file job spec')
        return 2
    spec_path = Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    button_data = Path(spec['button_data'])
    if str(button_data) not in sys.path:
        sys.path.insert(0, str(button_data))
    for name in [x for x in list(sys.modules) if x == 'core' or x.startswith('core.')]:
        sys.modules.pop(name, None)
    graft_mod = importlib.import_module('core.graft')
    skin_id = str(spec['skin_id'])
    files = spec['files']
    button_bundle = spec['button_bundle']
    out_bundle = spec['out_bundle']
    button_dir = spec['button_dir']
    out_dir = spec['work_dir']
    stages = [
        'Đang giải mã bundle gốc...',
        'Đang nạp Unity bundle...',
        'Đang graft FX...',
        'Đang graft joystick...',
        'Đang nén LZMA...',
        'Đang mã hóa bundle...',
        'Đang xử lý shop + hoàn tất ZIP...',
    ]
    stage_n = 0
    started = time.monotonic()
    def log(msg):
        emit('LOG', str(msg))
    def step():
        nonlocal stage_n
        stage_n += 1
        if stage_n <= len(stages):
            elapsed = time.monotonic() - started
            emit('STEP', json.dumps({'index': stage_n, 'total': len(stages), 'text': f'{stages[stage_n-1]} ({int(stage_n/len(stages)*100)}%)', 'elapsed': round(elapsed, 1)}))
    try:
        Path(out_bundle).parent.mkdir(parents=True, exist_ok=True)
        graft_mod.build_one(
            skin_id, files, button_bundle, out_bundle,
            log=log, step=step,
            button_dir=button_dir, out_dir=out_dir
        )
        emit('DONE', json.dumps({'elapsed': round(time.monotonic()-started, 1), 'out': out_bundle}))
        return 0
    except Exception as e:
        import traceback
        emit('ERROR', f'{type(e).__name__}: {e}')
        traceback.print_exc(file=sys.stdout)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
