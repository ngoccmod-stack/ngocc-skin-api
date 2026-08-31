from __future__ import annotations
import json, os, re, shutil, subprocess, tempfile, zipfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
AUTOMOD = ROOT / 'automod'
RESOURCES = ROOT / 'Resources'
BUILDS = ROOT / 'builds'
BUILDS.mkdir(parents=True, exist_ok=True)

CASEFIX = r'''
import builtins as _builtins
from pathlib import Path as _Path
_real_open = _builtins.open

def _ci_existing_path(path):
    try: p = _Path(path)
    except TypeError: return path
    if p.exists(): return path
    try:
        if p.is_absolute():
            cur = _Path(p.anchor); parts = p.parts[1:]
        else:
            cur = _Path.cwd(); parts = p.parts
        for part in parts:
            if not cur.exists() or not cur.is_dir(): return path
            exact = cur / part
            if exact.exists(): cur = exact; continue
            ms = [x for x in cur.iterdir() if x.name.casefold() == part.casefold()]
            if len(ms) != 1: return path
            cur = ms[0]
        return str(cur)
    except Exception: return path

def open(*args, **kwargs):
    mode = kwargs.get('mode', args[1] if len(args) > 1 else 'r') if args else kwargs.get('mode','r')
    if args and isinstance(mode, str) and ('r' in mode or '+' in mode):
        args = (_ci_existing_path(args[0]),) + args[1:]
    elif 'file' in kwargs and isinstance(mode,str) and ('r' in mode or '+' in mode):
        kwargs['file'] = _ci_existing_path(kwargs['file'])
    return _real_open(*args, **kwargs)
_builtins.open = open
'''


def find_active_version() -> Optional[str]:
    versions=[]
    for p in RESOURCES.iterdir() if RESOURCES.is_dir() else []:
        if p.is_dir() and (p/'Databin/Client/Actor/heroSkin.bytes').is_file() and (p/'Languages/VN_Garena_VN').is_dir():
            versions.append(p)
    if not versions: return None
    import re
    def k(p):
        out=[]
        for x in re.findall(r'\d+|[A-Za-z]+',p.name): out.append((0,int(x)) if x.isdigit() else (1,x.lower()))
        return out
    return sorted(versions,key=k)[-1].name


def build_skin(skin_id: str, resources_version: Optional[str] = None, display_name: Optional[str] = None) -> tuple[Path, str]:
    version = resources_version or find_active_version()
    if not version: raise RuntimeError('Chưa có Resources hợp lệ.')
    source = RESOURCES / version
    if not (source/'Databin/Client/Actor/heroSkin.bytes').is_file():
        raise RuntimeError(f'Resources {version} không hợp lệ.')
    with tempfile.TemporaryDirectory(prefix='ngocc_build_') as td:
        work=Path(td)
        (work/'Resources').mkdir()
        # Full resource tree is required by the existing AutoMod builder. Use a normal copy
        # so all writes made by Skin.py stay isolated from the master Resources.
        shutil.copytree(source, work/'Resources'/version, dirs_exist_ok=True)
        shutil.copytree(AUTOMOD/'FILES_CODE', work/'FILES_CODE', dirs_exist_ok=True)
        shutil.copytree(AUTOMOD/'FIX_SKIN', work/'FIX_SKIN', dirs_exist_ok=True)
        shutil.copy2(AUTOMOD/'Skin.py', work/'Skin.py')
        # Patch case-sensitive filename assumptions and enable one-shot web build.
        py=work/'Skin.py'; text=py.read_text(encoding='utf-8')
        marker='from pathlib import Path\n'
        # CASEFIX và khối WEB_BUILD_MODE được kiểm tra ĐỘC LẬP với nhau: Skin.py có thể
        # đã được vá WEB_BUILD_MODE từ trước (ví dụ do chỉnh tay) nhưng vẫn thiếu CASEFIX,
        # nên không được để việc "đã có WEB_BUILD_MODE" làm bỏ qua luôn việc vá CASEFIX.
        if '_ci_existing_path' not in text:
            text=text.replace(marker, marker+CASEFIX+'\n', 1)
        if 'WEB_BUILD_MODE = os.environ.get' not in text:
            ins=('resources_path = "Resources"\n\n'
                 'WEB_BUILD_MODE = os.environ.get("NGOCC_WEB_BUILD", "").lower() in {"1", "true", "yes"}\n'
                 'WEB_BUILD_ID = os.environ.get("NGOCC_WEB_BUILD_ID", "").strip()\n'
                 'WEB_BUILD_NAME = os.environ.get("NGOCC_WEB_BUILD_NAME", "").strip() or (WEB_BUILD_ID + " [DiaoChan]")\n'
                 'if WEB_BUILD_MODE:\n'
                 '    import builtins as _bm\n'
                 '    def _ngocc_input(prompt=""):\n'
                 '        p = str(prompt).lower()\n'
                 '        if "other function" in p: return "n"\n'
                 '        if "cách thức nhập id" in p: return "1"\n'
                 '        if "id skin" in p: return WEB_BUILD_ID\n'
                 '        if "enter skin pack name" in p: return WEB_BUILD_NAME.replace(" [DiaoChan]", "")\n'
                 '        if "mod component" in p: return "3"\n'
                 '        if "special: 54402" in p: return "n"\n'
                 '        if "thông báo hạ nakroth" in p and "use skin producer" in p: return "2"\n'
                 '        if "thông báo hạ:" in p: return "1"\n'
                 '        return "n"\n'
                 '    _bm.input = _ngocc_input\n')
            text=text.replace(marker, marker+ins, 1)
        if 'if WEB_BUILD_MODE:\n        break' not in text:
            text=text.replace('    print("\\033[1;97m[\\033[1;92m•\\033[1;97m] Done Mod")\n', '    print("\\033[1;97m[\\033[1;92m•\\033[1;97m] Done Mod")\n    if WEB_BUILD_MODE:\n        break\n', 1)
        py.write_text(text,encoding='utf-8')
        pack_name = (display_name or str(skin_id)).strip() or str(skin_id)
        env=os.environ.copy(); env.update(NGOCC_WEB_BUILD='1',NGOCC_WEB_BUILD_ID=str(skin_id),NGOCC_WEB_BUILD_NAME=f'{pack_name} [DiaoChan]',TERM='xterm')
        cp=subprocess.run([os.environ.get('PYTHON','python3'),'Skin.py'], cwd=work, env=env, text=True, capture_output=True, timeout=900)
        if cp.returncode != 0:
            # The patched one-shot builder completes before EOF only if an unexpected error occurs.
            raise RuntimeError((cp.stderr or cp.stdout)[-8000:])
        roots=[p for p in (work/'FILES_MOD').iterdir() if p.is_dir()] if (work/'FILES_MOD').exists() else []
        if not roots: raise RuntimeError('AutoMod không tạo được thư mục output.')
        root=roots[0]
        android=root/'Android/files'
        if not android.is_dir(): raise RuntimeError('AutoMod không tạo Android/files output.')
        # Không dùng root.name làm tên thư mục trong ZIP: AutoMod tự đặt tên bằng cách
        # đọc dữ liệu nhị phân, việc này không đáng tin cậy (có thể ra rỗng => "[DiaoChan]"
        # trơ trọi). Luôn dùng đúng tên tướng+skin đã biết từ catalog (pack_name) để đặt tên.
        out=BUILDS/f'{skin_id}_{version}.zip'
        tmp=out.with_suffix('.tmp')
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
            for f in android.rglob('*'):
                if not f.is_file():
                    continue
                if f.name.lower() == 'version.txt':
                    continue  # file thừa, không cần đóng gói theo yêu cầu
                rel = f.relative_to(android).as_posix()
                # Giữ đúng cấu trúc chuẩn: <Tên gói>/files/Resources/... (bỏ lớp "Android"
                # trung gian mà AutoMod tạo ra). Dùng pack_name (tên thật) thay vì root.name.
                z.write(f, f"{pack_name}/files/{rel}")
        tmp.replace(out)
        return out, version
