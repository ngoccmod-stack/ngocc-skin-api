from __future__ import annotations
import json, os, re, sys, time, traceback
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print('WORKER_ERROR: thiếu job json', flush=True)
        return 2
    job = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    skin_id = str(job['skin_id'])
    files = job['files']
    button_bundle = str(job['button_bundle'])
    out_path = Path(job['out_path'])
    button_dir = Path(job['button_dir'])
    out_dir = Path(job['out_dir'])
    pack_name = str(job['pack_name'])

    root = Path(__file__).resolve().parent
    data_root = root / 'button_resources'
    if str(data_root) not in sys.path:
        sys.path.insert(0, str(data_root))

    import core.graft as graft_mod

    started = time.monotonic()
    last_stage = {'n': 0}
    total = 7
    stages = [
        'Giải mã bundle gốc',
        'Nạp Unity bundle',
        'Graft FX',
        'Graft joystick',
        'Nén LZMA',
        'Mã hóa bundle',
        'Đóng ZIP',
    ]

    def log(msg):
        print(f'WORKER_LOG:{msg}', flush=True)

    def step():
        n = min(last_stage['n'] + 1, total)
        last_stage['n'] = n
        elapsed = time.monotonic() - started
        pct = int(n / total * 100)
        print(f'WORKER_STAGE:{n}|{total}|{pct}|{stages[n-1]}|{elapsed:.1f}', flush=True)

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        graft_mod.build_one(
            skin_id, files, button_bundle, str(out_path),
            log=log, step=step,
            button_dir=str(button_dir), out_dir=str(out_dir),
        )
        elapsed = time.monotonic() - started
        print(f'WORKER_DONE:{out_path}|{pack_name}.zip|{elapsed:.1f}', flush=True)
        return 0
    except Exception as e:
        print(f'WORKER_ERROR:{type(e).__name__}: {e}', flush=True)
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
