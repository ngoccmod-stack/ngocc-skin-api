import os as a, re as b, struct as i, tempfile as n, copy as f, colorsys as _colorsys
from .aovlib import UnityPy as j, decrypt_bundle as L, encrypt_bundle as M
try:
    from UnityPy_ForStudents.enums import TextureFormat as _TextureFormat
except Exception:
    try:
        from .aovlib.enums import TextureFormat as _TextureFormat
    except Exception:
        _TextureFormat = None
G = -1052576695779864424
K = -6778797527077953754
E = -7030229213176759517
s = -4848959964831355422
w = 6485305281367891218
B = -7503665643471169985
o = -2799986137220178741
I = -8806829761678967762
H = -4911661404432915893
D = -5387546953004491050
k = [6206484994098663942, -5634152749686239543]
O = {s: 'CustomJoyStick_RockingBg', B: 'CustomJoyStick_RockingArrow', I: 'CustomJoyStick_Decorate', H: 'CustomJoyStick_Decorate', D: 'CustomJoyStick_RockingBar'}
l = {'CustomJoyStick_Skill_FrameBg': 4521965459771754491, 'CustomJoyStick_Skill_FrameBg_Six': 6506458135070959965, 'CustomJoyStick_Skill_FrameBg_xi': -713949546598136875, 'CustomJoyStick_Skill_Projress_Big_1': -5395921638815586778, 'CustomJoyStick_Skill_Projress_Big_2': -4903935140751036718, 'CustomJoyStick_Skill_Projress_Big_3': -2959032211592467614, 'CustomJoyStick_Skill_Projress_Small_1': -8876048917458090228, 'CustomJoyStick_Skill_Projress_Small_2': -6999763066223432891, 'CustomJoyStick_Skill_Projress_Small_3': 5534646747319590423, 'CustomJoyStick_Skill_Projress_Small_4': -2422750244921060046, 'CustomJoyStick_Skill_Projress_Small_5': 1331825504267759371, 'CustomJoyStick_Skill_Projress_Small_6': -6695676195481413409, 'CustomJoyStick_AttackBtn': 3949139964913276237, 'CustomJoyStick_SoldierAttackBtn': -5915282664084471117, 'CustomJoyStick_OrganAttackBtn': 3742358440233270382, 'CustomJoyStick_LockHero': -1928409702755600487, 'CustomJoyStick_LockSoldier': -7893426383174433136, 'CustomJoyStick_LockBtnBg': -6298055555695112407}
x = 290.0
A = (164.0, 144.0)
C = 1.32
z = 90.0
F = set(l) | set(O.values())
v = {'Material', 'Texture2D', 'Shader', 'Mesh', 'AnimationClip', 'Sprite', 'Cubemap', 'Font', 'TextAsset', 'AudioClip', 'MonoScript', 'AvatarMask', 'RuntimeAnimatorController', 'AnimatorController', 'PhysicMaterial',
     # --- mo rong: sub-emitter cua ParticleSystem va cac node phu nam NGOAI cay
     # transform van phai duoc keo theo, neu khong FX se thieu manh.
     # ('AssetBundle' co y khong nam trong day: no tham chieu toi TAT CA object
     #  cua ca 6 bien the, follow vao la keo nguyen bundle.)
     'GameObject', 'Transform', 'RectTransform', 'ParticleSystem', 'ParticleSystemRenderer',
     'SortingGroup', 'MeshRenderer', 'MeshFilter', 'SkinnedMeshRenderer',
     'Animation', 'Animator', 'TrailRenderer', 'LineRenderer', 'CanvasRenderer'}


# ===== FX COLOR ENGINE v67 =====
FX_COLOR_PALETTE = [
    ('Đỏ đậm', '#8B0000'), ('Đỏ', '#FF0000'), ('Đỏ tươi', '#FF3B30'), ('Đỏ cam', '#FF5A36'),
    ('Cam đậm', '#D35400'), ('Cam', '#FF8A00'), ('Cam vàng', '#FFB300'),
    ('Vàng đậm', '#D4A017'), ('Vàng', '#FFD600'), ('Vàng nhạt', '#FFF176'),
    ('Xanh lá đậm', '#176B36'), ('Xanh lá', '#22C55E'), ('Xanh lá sáng', '#7CFF6B'),
    ('Xanh ngọc đậm', '#00897B'), ('Xanh ngọc', '#00C9A7'), ('Cyan', '#00E5FF'),
    ('Xanh dương đậm', '#123A8C'), ('Xanh dương', '#1677FF'), ('Xanh lam', '#42A5FF'),
    ('Xanh da trời', '#80D8FF'), ('Xanh navy', '#172554'),
    ('Tím đậm', '#4C1D95'), ('Tím', '#7C3AED'), ('Tím sáng', '#A855F7'),
    ('Tím hồng', '#C026D3'), ('Hồng đậm', '#DB2777'), ('Hồng', '#FF4FA3'),
    ('Hồng sáng', '#FF80C8'), ('Hồng phấn', '#FFC1E3'),
    ('Nâu đậm', '#5C3A21'), ('Nâu', '#A66A3F'), ('Be', '#D8B48A'),
    ('Đen', '#000000'), ('Xám đậm', '#404040'), ('Xám', '#808080'),
    ('Xám nhạt', '#BDBDBD'), ('Trắng', '#FFFFFF'),
]

def _mix_rgb(items):
    total = sum(float(w) for _, w in items)
    if total <= 0: raise ValueError('Tổng tỷ lệ màu phải lớn hơn 0')
    return tuple(sum(float(c[k])*float(w) for c,w in items)/total for k in range(3))

def _gray_kind(h,s,v):
    if s >= .10: return None
    if v <= .20: return 'black'
    if v >= .80: return 'white'
    return 'gray'

def _transform_fx_image(img, spec):
    img=img.convert('RGBA')
    mode=spec.get('mode'); target=spec.get('target_rgb'); mix=spec.get('mix_rgb')
    selected_hues=spec.get('selected_hues'); gray_targets=set(spec.get('gray_targets') or [])
    t01=tuple(float(v)/255 for v in target) if target else None
    m01=tuple(float(v)/255 for v in mix) if mix else None
    out=[]
    for r,g,b,a in img.getdata():
        if a==0: out.append((r,g,b,a)); continue
        rf,gf,bf=r/255,g/255,b/255; h,s,v=_colorsys.rgb_to_hsv(rf,gf,bf); gray=_gray_kind(h,s,v)
        apply = (gray in gray_targets) if gray else (selected_hues is None or any(abs(h-sh)<.05 for sh in selected_hues))
        if not apply: out.append((r,g,b,a)); continue
        if mode=='replace' and t01 is not None:
            th,ts,tv=_colorsys.rgb_to_hsv(*t01)
            nr,ng,nb = t01 if ts<.08 else _colorsys.hsv_to_rgb(th,max(s,ts),v if gray is None else tv)
        elif mode=='mix' and m01 is not None:
            mh,ms,mv=_colorsys.rgb_to_hsv(*m01)
            nr,ng,nb = m01 if ms<.08 else _colorsys.hsv_to_rgb(mh,max(s,ms),v if gray is None else mv)
        else: nr,ng,nb=rf,gf,bf
        out.append((int(max(0,min(1,nr))*255),int(max(0,min(1,ng))*255),int(max(0,min(1,nb))*255),a))
    img.putdata(out); return img


# ===== COLOR WORKFLOW (uses the same UnityPy_AOV + PIL workflow as the user's Texture2D tool) =====
def _import_color_backend():
    """Use the Button Tool's own UnityPy bundle reader, but replace its local
    decoder stubs with the real pip decoders used by the working Texture2D tool.

    The important distinction is:
      * bundle/container parsing stays on the proven AOV fork in ``lib/UnityPy``;
      * texture ETC/ASTC/ETC2 decode + encode uses the real ``texture2ddecoder`` /
        ``etcpak`` packages, not the tiny NotImplemented stubs shipped in this tool.
    """
    import sys as _sys, importlib as _importlib

    # ``core.aovlib`` already imported the proven AOV UnityPy fork.
    _ua = j

    # The AOV tool intentionally ships tiny local decoder stubs in lib/.  They are
    # useful as placeholders for the graft engine, but must not be used by the
    # colour workflow.  Temporarily hide every path whose basename is ``lib`` and
    # remove already-loaded stub modules so Python resolves the real pip packages.
    old_path = list(_sys.path)
    try:
        _sys.path[:] = [pp for pp in _sys.path
                        if not (pp and a.path.basename(a.path.normpath(pp)) == 'lib')]
        for name in ('texture2ddecoder', 'etcpak'):
            mod = _sys.modules.get(name)
            if mod is not None:
                origin = str(getattr(mod, '__file__', '') or '')
                if '/lib/' in origin.replace('\\', '/') or origin.endswith('/lib'):
                    del _sys.modules[name]
        decoder = _importlib.import_module('texture2ddecoder')
        encoder = _importlib.import_module('etcpak')

        # UnityPy's Texture2DConverter captured whatever modules were available
        # when the tool imported it. Replace those bindings in-place.
        try:
            conv = _ua.export.Texture2DConverter
        except Exception:
            conv = _importlib.import_module('UnityPy.export.Texture2DConverter')
        conv.texture2ddecoder = decoder
        conv.etcpak = encoder

        return _ua, _ua.enums.TextureFormat
    except Exception as ex:
        raise RuntimeError(
            'Khong tim thay bo decoder dang dung cua Texture2D Tool. '
            'Can texture2ddecoder + etcpak: %s' % ex)
    finally:
        _sys.path[:] = old_path


def _color_bundle_envs(effect_path, raw_path, work_dir):
    """Open the EFFECT bundles exactly like the working Texture2D pipeline.

    The button Tool's proven AOV UnityPy reader is used for the UnityFS container;
    the real texture codecs are injected by ``_import_color_backend`` above.
    """
    ua, _tf = _import_color_backend()
    bundles=[]
    if effect_path and a.path.isfile(effect_path):
        bundles.append(('effect', effect_path, ua.load(effect_path)))
    if raw_path and a.path.isfile(raw_path):
        bundles.append(('raw', raw_path, ua.load(raw_path)))
    return ua, bundles


def _color_texture_key(kind, obj):
    return '%s:%s' % (kind, int(getattr(obj, 'path_id', 0) or 0))


def _apply_color_to_image_exact(img, spec):
    return _transform_fx_image(img, spec)


def scan_fx_texture_catalog_aov(effect_path, raw_path=None, work_dir=None):
    cleanup=None
    base=work_dir or n.mkdtemp(prefix='aov_fx_color_aovscan_')
    if work_dir is None: cleanup=base
    rows=[]
    try:
        _ua, bundles = _color_bundle_envs(effect_path, raw_path, base)
        for kind, _path, env in bundles:
            for obj in env.objects:
                if obj.type.name != 'Texture2D':
                    continue
                try:
                    data=obj.read(); img=data.image.convert('RGBA'); bins={}
                    for rr,gg,bb,aa in img.getdata():
                        if aa==0: continue
                        h,ss,vv=_colorsys.rgb_to_hsv(rr/255,gg/255,bb/255)
                        if ss>=.10: bins[round(h,2)]=bins.get(round(h,2),0)+1
                    hues=[h for h,_ in sorted(bins.items(),key=lambda kv:kv[1],reverse=True)[:8]]
                    name=str(getattr(data,'m_Name','') or 'Texture2D_%s'%obj.path_id)
                    rows.append({'key':_color_texture_key(kind,obj),'bundle':kind,'path_id':int(obj.path_id),'name':name,'hues':hues,'format':str(getattr(data,'m_TextureFormat',''))})
                except Exception as ex:
                    name='Texture2D_%s'%obj.path_id
                    rows.append({'key':_color_texture_key(kind,obj),'bundle':kind,'path_id':int(obj.path_id),'name':name,'hues':[],'format':'', 'error':type(ex).__name__})
    finally:
        if cleanup:
            import shutil; shutil.rmtree(cleanup,ignore_errors=True)
    return rows


def preprocess_effect_color(effect_path, raw_path, work_dir, spec, log=lambda s: None):
    """Recolor only the EFFECT bundle's Texture2D dependencies.

    Source bundles are never modified in place.  The raw texture bundle is normally
    where the actual FX textures live; the main effect bundle is copied unchanged
    when it contains no Texture2D.  This mirrors the successful manual workflow:
    export Texture2D -> recolour PNG pixels -> import as RGBA32 -> save -> encrypt.
    """
    if not spec or spec.get('keep') or spec.get('mode') not in ('replace','mix'):
        return effect_path, raw_path
    try:
        ua, bundles = _color_bundle_envs(effect_path, raw_path, work_dir)
        _ua_tf = ua.enums.TextureFormat.RGBA32
    except Exception as ex:
        raise RuntimeError('Khong the mo Color backend UnityPy/decoder: %s' % ex)

    allowed=set(spec.get('texture_keys') or [])
    changed_total=0; skipped_total=0
    out_paths={}

    for kind, src_path, env in bundles:
        tex_count=0
        tex_changed=0
        for obj in env.objects:
            if obj.type.name != 'Texture2D':
                continue
            tex_count += 1
            key=_color_texture_key(kind,obj)
            if allowed and key not in allowed:
                continue
            try:
                data=obj.read()
                img=data.image.convert('RGBA')
                new=_apply_color_to_image_exact(img,spec)
                data.set_image(new, _ua_tf)
                data.save()
                changed_total += 1
                tex_changed += 1
            except Exception as ex:
                skipped_total += 1
                log('   ! COLOR Texture2D %s bo qua: %s' % (getattr(obj,'path_id','?'), type(ex).__name__))

        # Save an intermediate bundle and re-apply the AOV protection only when
        # the bundle actually participated in the color pipeline.  This keeps the
        # source bundle untouched while letting graft.py consume the temp copy.
        tag='effect' if kind=='effect' else 'raw'
        if tex_count or kind == 'effect':
            std=a.path.join(work_dir, tag+'_color_mod.assetbundle')
            with open(std,'wb') as fh:
                fh.write(env.file.save('lz4'))
            enc=a.path.join(work_dir, tag+'_color_mod_enc.assetbundle')
            M(std,enc)
            out_paths[kind]=enc
        log('   COLOR-AOV %s: %d Texture2D, %d doi mau' % (kind.upper(), tex_count, tex_changed))

    log('   COLOR-AOV tong: %d Texture2D doi mau; %d bo qua' % (changed_total, skipped_total))
    return out_paths.get('effect', effect_path), out_paths.get('raw', raw_path)

def scan_fx_texture_catalog_aov(effect_path, raw_path=None, work_dir=None):
    cleanup=None
    base=work_dir or n.mkdtemp(prefix='aov_fx_color_aovscan_')
    if work_dir is None: cleanup=base
    rows=[]
    try:
        _ua, bundles = _color_bundle_envs(effect_path, raw_path, base)
        for kind, _path, env in bundles:
            for obj in env.objects:
                if obj.type.name != 'Texture2D':
                    continue
                try:
                    data=obj.read(); img=data.image.convert('RGBA'); bins={}
                    for rr,gg,bb,aa in img.getdata():
                        if aa==0: continue
                        h,ss,vv=_colorsys.rgb_to_hsv(rr/255,gg/255,bb/255)
                        if ss>=.10: bins[round(h,2)]=bins.get(round(h,2),0)+1
                    hues=[h for h,_ in sorted(bins.items(),key=lambda kv:kv[1],reverse=True)[:8]]
                    name=str(getattr(data,'m_Name','') or 'Texture2D_%s'%obj.path_id)
                    rows.append({'key':_color_texture_key(kind,obj),'bundle':kind,'path_id':int(obj.path_id),'name':name,'hues':hues,'format':str(getattr(data,'m_TextureFormat',''))})
                except Exception as ex:
                    name='Texture2D_%s'%obj.path_id
                    rows.append({'key':_color_texture_key(kind,obj),'bundle':kind,'path_id':int(obj.path_id),'name':name,'hues':[],'format':str(getattr(obj.read(), 'm_TextureFormat','')) if False else '', 'error':type(ex).__name__})
    finally:
        if cleanup:
            import shutil; shutil.rmtree(cleanup,ignore_errors=True)
    return rows


def preprocess_effect_color(effect_path, raw_path, work_dir, spec, log=lambda s: None):
    """Recolor the EFFECT bundle using the same workflow as the user's Texture2D tool.

    The tool's working method is: decrypt -> load with UnityPy_AOV -> Texture2D.image
    -> PIL pixel edit -> set_image(..., RGBA32) -> save -> encrypt. Both the main effect
    bundle and its *_raw texture bundle are handled, and Sprite/JOYSTICK assets are never touched.
    Returns (new_effect_path, new_raw_path).
    """
    if not spec or spec.get('keep') or spec.get('mode') not in ('replace','mix'):
        return effect_path, raw_path
    try:
        ua, bundles = _color_bundle_envs(effect_path, raw_path, work_dir)
        _ua_tf = ua.enums.TextureFormat.RGBA32
    except Exception as ex:
        raise RuntimeError('Khong the mo Color backend UnityPy_AOV: %s' % ex)
    allowed=set(spec.get('texture_keys') or [])
    changed_total=0; skipped_total=0
    out_paths={}
    for kind, dec_path, env in bundles:
        for obj in env.objects:
            if obj.type.name != 'Texture2D':
                continue
            key=_color_texture_key(kind,obj)
            if allowed and key not in allowed:
                continue
            try:
                data=obj.read()
                img=data.image.convert('RGBA')
                new=_apply_color_to_image_exact(img,spec)
                # Match texture.py: force RGBA32 on import after PIL processing.
                data.set_image(new, _ua_tf)
                data.save()
                changed_total += 1
            except Exception as ex:
                skipped_total += 1
                log('   ! COLOR-AOV Texture2D %s bo qua: %s' % (getattr(obj,'path_id','?'), type(ex).__name__))
        tag='effect' if kind=='effect' else 'raw'
        std=a.path.join(work_dir, tag+'_color_mod.assetbundle')
        with open(std,'wb') as fh:
            fh.write(env.file.save('lz4'))
        enc=a.path.join(work_dir, tag+'_color_mod_enc.assetbundle')
        M(std,enc)
        out_paths[kind]=enc
    log('   COLOR-AOV: %d Texture2D doi mau; %d bo qua' % (changed_total, skipped_total))
    return out_paths.get('effect', effect_path), out_paths.get('raw', raw_path)

def scan_fx_texture_catalog(effect_path, raw_path=None, work_dir=None):
    cleanup=None; base=work_dir or n.mkdtemp(prefix='aov_fx_color_scan_')
    if work_dir is None: cleanup=base
    rows=[]
    try:
        env,_=g(effect_path,base,'fxcolorscan.assetbundle'); seen=set()
        for obj in env.objects:
            if obj.type.name!='Texture2D' or obj.path_id in seen: continue
            seen.add(obj.path_id)
            try:
                data=obj.read(); img=data.image.convert('RGBA'); bins={}
                for rr,gg,bb,aa in img.getdata():
                    if aa==0: continue
                    h,s,v=_colorsys.rgb_to_hsv(rr/255,gg/255,bb/255)
                    if s>=.10: bins[round(h,2)]=bins.get(round(h,2),0)+1
                hues=[h for h,_ in sorted(bins.items(),key=lambda kv:kv[1],reverse=True)[:5]]
                rows.append({'path_id':int(obj.path_id),'name':str(getattr(data,'m_Name','') or 'Texture2D_%s'%obj.path_id),'hues':hues})
            except Exception:
                rows.append({'path_id':int(obj.path_id),'name':'Texture2D_%s'%obj.path_id,'hues':[]})
    finally:
        if cleanup:
            import shutil; shutil.rmtree(cleanup,ignore_errors=True)
    return rows

def _color_pixel_rgb(rgb, spec):
    r, g, b = rgb
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    h, sat, val = _colorsys.rgb_to_hsv(rf, gf, bf)
    gray = _gray_kind(h, sat, val)
    gray_targets = set(spec.get('gray_targets') or [])
    if gray is not None:
        apply = gray in gray_targets
    else:
        selected_hues = spec.get('selected_hues')
        apply = selected_hues is None or any(abs(h - sh) < 0.05 for sh in selected_hues)
    if not apply:
        return r, g, b, False
    target = spec.get('target_rgb')
    if spec.get('mode') == 'replace' and target:
        tr, tg, tb = [float(v) / 255.0 for v in target]
        th, ts, tv = _colorsys.rgb_to_hsv(tr, tg, tb)
        nr, ng, nb = (tr, tg, tb) if ts < 0.08 else _colorsys.hsv_to_rgb(th, max(sat, ts), val if gray is None else tv)
    else:
        mix = spec.get('mix_rgb')
        if not mix:
            return r, g, b, False
        mr, mg, mb = [float(v) / 255.0 for v in mix]
        mh, ms, mv = _colorsys.rgb_to_hsv(mr, mg, mb)
        nr, ng, nb = (mr, mg, mb) if ms < 0.08 else _colorsys.hsv_to_rgb(mh, max(sat, ms), val if gray is None else mv)
    return int(nr * 255), int(ng * 255), int(nb * 255), True

def _material_refers_to_texture(tree, tex_obj):
    target_pid = int(getattr(tex_obj, 'path_id', 0) or 0)
    if target_pid == 0 or not isinstance(tree, dict):
        return False
    def walk(v):
        if isinstance(v, dict):
            if 'm_FileID' in v and 'm_PathID' in v:
                try:
                    if int(v.get('m_PathID', 0)) == target_pid:
                        return True
                except Exception:
                    pass
                return False
            return any(walk(x) for x in v.values())
        if isinstance(v, (list, tuple)):
            return any(walk(x) for x in v)
        return False
    return walk(tree)


def _tint_material(mat_obj, spec, log=lambda s: None):
    """Tint every color property a selected FX material exposes.

    This is the fallback for compressed ETC/ASTC textures that this UnityPy fork
    cannot decode. FX materials are already cloned from the source effect, so
    changing these properties only affects the cloned FX material.
    """
    try:
        tree = mat_obj.read_typetree()
        if not isinstance(tree, dict):
            return False
        saved = tree.get('m_SavedProperties') or {}
        colors = saved.get('m_Colors') or []
        changed = False
        for entry in colors:
            if not isinstance(entry, dict):
                continue
            key = entry.get('first')
            col = entry.get('second')
            if not isinstance(col, dict):
                continue
            # Only touch shader color properties, not arbitrary serialized values.
            key_s = str(key or '')
            if key_s and ('color' not in key_s.lower()) and key_s not in ('_Color', '_TintColor', '_MainColor', '_BaseColor'):
                continue
            try:
                rgba = (
                    int(max(0, min(1, float(col.get('r', 1.0)))) * 255),
                    int(max(0, min(1, float(col.get('g', 1.0)))) * 255),
                    int(max(0, min(1, float(col.get('b', 1.0)))) * 255),
                )
            except Exception:
                continue
            nr, ng, nb, do_change = _color_pixel_rgb(rgba, spec)
            if do_change:
                col['r'] = nr / 255.0
                col['g'] = ng / 255.0
                col['b'] = nb / 255.0
                changed = True
        if changed:
            mat_obj.save_typetree(tree)
        return changed
    except Exception as ex:
        log('   ! COLOR Material %s fallback loi: %s' % (getattr(mat_obj, 'path_id', '?'), ex))
        return False

def apply_fx_color(_objects, _spec, _materials=None, _log=lambda s: None):
    """Color selected FX.

    1) Decode/rewrite readable Texture2D.
    2) ALWAYS tint the FX's cloned Material color properties as a fallback/overlay.
       This is important for ETC1/ETC2/ASTC textures which cannot be decoded by the
       bundled UnityPy fork. Materials are scoped to this FX only.
    """
    if not _spec or _spec.get('keep') or _spec.get('mode') not in ('replace', 'mix'):
        return 0
    count = 0
    material_count = 0
    seen = set()
    allowed = set(_spec.get('texture_names') or [])
    decoded_failed = []
    for obj in _objects:
        if obj is None or getattr(obj.type, 'name', '') != 'Texture2D' or obj.path_id in seen:
            continue
        seen.add(obj.path_id)
        try:
            data = obj.read()
            name = str(getattr(data, 'm_Name', '') or '')
            if allowed and name not in allowed:
                continue
            img = data.image.convert('RGBA')
            new = _transform_fx_image(img, _spec)
            try:
                data.set_image(new, _TextureFormat.RGBA32 if _TextureFormat is not None else None)
            except TypeError:
                data.set_image(new)
            data.save()
            count += 1
        except Exception as ex:
            decoded_failed.append(obj)
            _log('   ! COLOR Texture2D %s bo qua decode: %s' % (getattr(obj, 'path_id', '?'), getattr(ex, '__class__', type(ex)).__name__))

    # Material fallback is not tied to failed texture PPtrs anymore. For selected FX,
    # tint all its own Material color properties so compressed textures still visibly react.
    if _materials:
        for mat in _materials:
            try:
                if _tint_material(mat, _spec, _log):
                    material_count += 1
            except Exception:
                pass

    if decoded_failed:
        _log('   COLOR: %d Texture2D doi mau; %d texture khong decode duoc -> dung Material tint' % (count, len(decoded_failed)))
    else:
        _log('   COLOR: %d Texture2D da doi mau' % count)
    if material_count:
        _log('   COLOR: %d Material FX da tint' % material_count)
    return count + material_count

def list_fx_texture_catalog(effect_path, raw_path=None, work_dir=None):
    """List every Texture2D in the effect without requiring pixel decoding."""
    cleanup = None
    base = work_dir or n.mkdtemp(prefix='aov_fx_texture_list_')
    if work_dir is None:
        cleanup = base
    rows = []
    try:
        env, _ = g(effect_path, base, 'fxtexturelist.assetbundle')
        seen = set()
        for obj in env.objects:
            if obj.type.name != 'Texture2D' or obj.path_id in seen:
                continue
            seen.add(obj.path_id)
            name = 'Texture2D_%s' % obj.path_id
            fmt = ''
            try:
                tree = obj.read_typetree()
                name = str(tree.get('m_Name') or name)
                fmt = str(tree.get('m_TextureFormat') or tree.get('m_CompleteImageSize') or '')
            except Exception:
                try:
                    data = obj.read()
                    name = str(getattr(data, 'm_Name', '') or name)
                except Exception:
                    pass
            rows.append({'path_id': int(obj.path_id), 'name': name, 'format': fmt})
    finally:
        if cleanup:
            import shutil
            shutil.rmtree(cleanup, ignore_errors=True)
    return rows

class t(Exception):
    pass

def h(S):
    R = object.__new__(type(S))
    R.__dict__.update(S.__dict__)
    R.data = b''
    return R

def e(R):
    return bytes(R.get_raw_data())

def y(T, U):
    if isinstance(T, dict):
        if 'm_FileID' in T and 'm_PathID' in T:
            R = (T['m_FileID'], T['m_PathID'])
            if R in U:
                T['m_FileID'] = 0
                T['m_PathID'] = U[R]
            return T
        for S in T.values():
            y(S, U)
    elif isinstance(T, (list, tuple)):
        for S in T:
            y(S, U)
    return T

def Q(T):
    if isinstance(T, dict):
        if 'm_FileID' in T and 'm_PathID' in T:
            R, S = (T['m_FileID'], T['m_PathID'])
            if isinstance(R, int) and isinstance(S, int) and (S != 0):
                yield (R, S)
            return
        for U in T.values():
            yield from Q(U)
    elif isinstance(T, (list, tuple)):
        for U in T:
            yield from Q(U)

def d(R):
    try:
        return R.read_typetree()
    except Exception:
        return None

def c(R):
    return list(R.objects)[0].assets_file

def p(R, T, V=None):
    S = T
    U = R.objects
    while S == 0 or S in U or (V is not None and S in V):
        S += 1
    if V is not None:
        V.add(S)
    return S

def g(T, U, S):
    R = a.path.join(U, S)
    L(T, R)
    return (j.load(R), R)

def u(W, Y, X=None):
    S = len(W)
    R = 0
    while R <= S - 12:
        T = i.unpack_from('<i', W, R)[0]
        if 0 <= T <= 32:
            V = i.unpack_from('<q', W, R + 4)[0]
            if V != 0:
                U = Y(T, V)
                if U is not None and (X is None or X(T, V, U)):
                    yield (R, T, V)
                    R += 12
                    continue
        R += 1

def q(S, Y, X=None):
    W = d(S)
    if W is not None:
        for T, V in Q(W):
            U = Y(T, V)
            if U is not None and (X is None or X(T, V, U)):
                yield (T, V)
        return
    for R, T, V in u(e(S), Y, X):
        yield (T, V)

def J(R, X, Z):
    ab = d(R)
    if ab is None:
        return None
    ad = {}
    for S, W in Q(ab):
        if Z(S, W):
            ad[S, W] = ad.get((S, W), 0) + 1
    U = []
    aa = bytes(X)
    for (S, W), ac in ad.items():
        V = i.pack('<iq', S, W)
        Y = [T for T in range(0, len(aa) - 11, 4) if aa[T:T + 12] == V]
        if len(Y) != ac:
            raise t('khong dinh vi chinh xac PPtr %s:%s trong %s (tree=%d, raw=%d)' % (S, W, R.type.name, ac, len(Y)))
        U.extend(((af, S, W) for af in Y))
    return U

def r(R):
    S = getattr(R, 'serialized_type', None)
    return (R.class_id, getattr(S, 'script_id', None), getattr(S, 'old_type_hash', None))

def _v3(T, key, default=0.0):
    V = T.get(key) if isinstance(T, dict) else None
    if not isinstance(V, dict):
        return (default, default, default)
    return (float(V.get('x', default)), float(V.get('y', default)), float(V.get('z', default)))

def _quat(T, key):
    V = T.get(key) if isinstance(T, dict) else None
    if not isinstance(V, dict):
        return (0.0, 0.0, 0.0, 1.0)
    return (float(V.get('x', 0.0)), float(V.get('y', 0.0)), float(V.get('z', 0.0)), float(V.get('w', 1.0)))

def _qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw,
            aw*bw - ax*bx - ay*by - az*bz)

def _qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    # q * v * q^-1, specialized
    tx = 2.0 * (y*vz - z*vy)
    ty = 2.0 * (z*vx - x*vz)
    tz = 2.0 * (x*vy - y*vx)
    return (vx + w*tx + (y*tz - z*ty),
            vy + w*ty + (z*tx - x*tz),
            vz + w*tz + (x*ty - y*tx))

def _compose_source_root(root_t, child_t):
    rp = _v3(root_t, 'm_LocalPosition')
    rs = _v3(root_t, 'm_LocalScale', 1.0)
    rr = _quat(root_t, 'm_LocalRotation')
    cp = _v3(child_t, 'm_LocalPosition')
    cr = _quat(child_t, 'm_LocalRotation')
    cs = _v3(child_t, 'm_LocalScale', 1.0)
    scaled = (cp[0]*rs[0], cp[1]*rs[1], cp[2]*rs[2])
    rp2 = _qrot(rr, scaled)
    pos = {'x': rp[0]+rp2[0], 'y': rp[1]+rp2[1], 'z': rp[2]+rp2[2]}
    rot = _qmul(rr, cr)
    scale = {'x': rs[0]*cs[0], 'y': rs[1]*cs[1], 'z': rs[2]*cs[2]}
    return pos, rot, scale

def get_fx_size(effect_path, raw_path=None, work_dir=None):
    """Return the source FX child local X scale (the value shown as original size)."""
    cleanup = None
    base = work_dir or n.mkdtemp(prefix='aov_fx_info_')
    if work_dir is None:
        cleanup = base
    try:
        env, _ = g(effect_path, base, 'fxinfo.assetbundle')
        assets = list(env.objects)
        af = assets[0].assets_file if assets else None
        if af is None:
            return 1.0
        for obj in assets:
            if obj.type.name not in ('Transform', 'RectTransform'):
                continue
            tr = d(obj)
            if not tr or tr.get('m_Father', {}).get('m_PathID') != 0:
                continue
            go = af.objects.get(tr.get('m_GameObject', {}).get('m_PathID'))
            gd = d(go) if go else None
            if gd and str(gd.get('m_Name', '')).lower() == 'attackbutton':
                ch = tr.get('m_Children') or []
                if not ch:
                    break
                child = af.objects.get(ch[0]['m_PathID'])
                ct = d(child) if child else None
                if ct:
                    sc = ct.get('m_LocalScale') or {}
                    return float(sc.get('x', 1.0))
        return 1.0
    finally:
        if cleanup:
            import shutil
            shutil.rmtree(cleanup, ignore_errors=True)


def get_fx_anchor(effect_path, work_dir=None):
    """Return the source button FX child local Transform used as the alignment reference.

    The first child under the source AttackButton is the FX child that the tool mounts.
    We use its local transform as the source-space anchor so secondary FX can be aligned
    relative to the skin used for the button itself.
    """
    cleanup = None
    base = work_dir or n.mkdtemp(prefix='aov_fx_anchor_')
    if work_dir is None:
        cleanup = base
    try:
        env, _ = g(effect_path, base, 'fxanchor.assetbundle')
        af = c(env)
        for obj in env.objects:
            if obj.type.name not in ('Transform', 'RectTransform'):
                continue
            tr = d(obj)
            if not isinstance(tr, dict) or tr.get('m_Father', {}).get('m_PathID') != 0:
                continue
            go = af.objects.get(tr.get('m_GameObject', {}).get('m_PathID'))
            gd = d(go) if go else None
            if not gd or str(gd.get('m_Name', '')).lower() != 'attackbutton':
                continue
            children = tr.get('m_Children') or []
            if not children:
                break
            child = af.objects.get(children[0].get('m_PathID'))
            ct = d(child) if child else None
            if not isinstance(ct, dict):
                break
            return {
                'position': copy.deepcopy(ct.get('m_LocalPosition') or {'x': 0.0, 'y': 0.0, 'z': 0.0}),
                'rotation': copy.deepcopy(ct.get('m_LocalRotation') or {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}),
                'scale': copy.deepcopy(ct.get('m_LocalScale') or {'x': 1.0, 'y': 1.0, 'z': 1.0}),
            }
        return {'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'rotation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
                'scale': {'x': 1.0, 'y': 1.0, 'z': 1.0}}
    finally:
        if cleanup:
            import shutil
            shutil.rmtree(cleanup, ignore_errors=True)

def m(bl, bo, bw, bb, az=lambda s: None, append=False, size_override=None, layer_index=1, layer_count=1, mount_children=None, unique_namespace=False, keep_default=False, default_layer=1, reference_anchor=None, is_reference_fx=False, color_spec=None):
    aM = c(bl)
    R = aM.objects
    bd, S = g(bo, bb, 'eff.assetbundle')
    aT = {0: {Z.path_id: Z for Z in bd.objects}}
    br = {}
    aL = c(bd)
    for ax, ah in enumerate(aL.externals, start=1):
        br[ax] = ah.path
    if bw and a.path.isfile(bw):
        bg, S = g(bw, bb, 'effraw.assetbundle')
        bf = c(bg).name if hasattr(c(bg), 'name') else ''
        bp = {Z.path_id: Z for Z in bg.objects}
        for ax, aa in br.items():
            if bf and bf in aa:
                aT[ax] = bp
                break
        else:
            for ax in br:
                if ax not in aT:
                    aT[ax] = bp
                    break

    def bh(by, bz):
        bx = aT.get(by)
        return bx.get(bz) if bx else None
    aI = None
    for aC, Z in aT[0].items():
        if Z.type.name not in ('Transform', 'RectTransform'):
            continue
        U = d(Z)
        if not U or U['m_Father']['m_PathID'] != 0:
            continue
        V = aT[0].get(U['m_GameObject']['m_PathID'])
        aj = d(V) if V else None
        if aj and str(aj.get('m_Name', '')).lower() == 'attackbutton':
            aI = (aC, Z, U)
            break
    if aI is None:
        raise t("khong tim thay root 'AttackButton' trong file effect")
    aJ, aH, ao = aI
    if len(ao['m_Children']) != 1:
        raise t('root co %d child (mong doi 1)' % len(ao['m_Children']))
    # Mount truc tiep child FX thay vi root AttackButton.
    # Neu mount ca root roi lai giu localPosition cua child 'Effect' ben trong,
    # game se cong offset 2 lan -> qua cau bi lech tam va trong qua to.
    aW = ao['m_Children'][0]['m_PathID']
    # Giữ nguyên Transform của child FX đúng như assetbundle skin gốc.
    # Không cộng Transform của root AttackButton: child được mount trực tiếp
    # vào effect của battleotherui nên cộng root sẽ tạo offset kép.
    _source_child_t = d(aT[0].get(aW)) or {}
    _source_pos = _source_child_t.get('m_LocalPosition') or {'x': 0.0, 'y': 0.0, 'z': 0.0}
    _source_rot = _source_child_t.get('m_LocalRotation') or {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
    _source_scale = _source_child_t.get('m_LocalScale') or {'x': 1.0, 'y': 1.0, 'z': 1.0}
    # Secondary FX: use the source skin that drives the button as the position origin.
    # The primary/reference skin is known to align correctly, so each additional FX is
    # placed by its source offset relative to that reference rather than using its own
    # absolute source position blindly. The primary layer itself remains untouched.
    if reference_anchor and not is_reference_fx:
        _refp = reference_anchor.get('position') or {'x': 0.0, 'y': 0.0, 'z': 0.0}
        _source_pos = {
            'x': float(_source_pos.get('x', 0.0)) - float(_refp.get('x', 0.0)),
            'y': float(_source_pos.get('y', 0.0)) - float(_refp.get('y', 0.0)),
            'z': float(_source_pos.get('z', 0.0)) - float(_refp.get('z', 0.0)),
        }
        az('   ALIGN: layer %d position relative to button skin reference (%.6g, %.6g, %.6g)' % (
            int(layer_index), _refp.get('x', 0.0), _refp.get('y', 0.0), _refp.get('z', 0.0)))
    aF = set()
    aU = [aW]
    while aU:
        aq = aU.pop()
        if aq in aF:
            continue
        Z = aT[0].get(aq)
        if Z is None:
            continue
        U = d(Z)
        if U is None:
            continue
        aF.add(aq)
        ak = U['m_GameObject']['m_PathID']
        if ak and ak not in aF:
            aF.add(ak)
            aj = d(aT[0][ak])
            if aj:
                for T in aj.get('m_Component', []):
                    ae = T['component']['m_PathID']
                    if ae:
                        aF.add(ae)
        for T in U.get('m_Children', []):
            aU.append(T['m_PathID'])
    bn = [aa for aa in list(aF) if aT[0].get(aa) is not None and aT[0][aa].type.name not in ('GameObject', 'Transform', 'RectTransform')]
    aP = {}
    aO = [(0, aa) for aa in bn]
    aK = set(aO)
    while aO:
        au, aC = aO.pop()
        Z = bh(au, aC)
        if Z is None:
            continue
        for ai, am in q(Z, bh, lambda bx, by, bz: bz.type.name in v):
            al = bh(ai, am)
            X = (ai, am)
            if X in aP or (ai == 0 and am in aF):
                continue
            aP[X] = al
            if X not in aK:
                aK.add(X)
                aO.append(X)
    if color_spec and not color_spec.get('keep'):
        _fx_texture_objs=[]; _seen_tex=set()
        for _src_obj in list(aF)+[(_x[1]) for _x in aP.keys()]:
            _tex_obj=aT[0].get(_src_obj) if isinstance(_src_obj,int) else None
            if _tex_obj is not None and _tex_obj.type.name=='Texture2D' and _tex_obj.path_id not in _seen_tex:
                _fx_texture_objs.append(_tex_obj); _seen_tex.add(_tex_obj.path_id)
        for _ext_pid,_ext_obj in aP.items():
            if _ext_obj is not None and _ext_obj.type.name=='Texture2D' and _ext_obj.path_id not in _seen_tex:
                _fx_texture_objs.append(_ext_obj); _seen_tex.add(_ext_obj.path_id)
        _fx_material_objs = []
        _seen_mat = set()
        for _src_obj in list(aF) + [(_x[1]) for _x in aP.keys()]:
            _mobj = aT[0].get(_src_obj) if isinstance(_src_obj, int) else None
            if _mobj is not None and _mobj.type.name == 'Material' and _mobj.path_id not in _seen_mat:
                _fx_material_objs.append(_mobj); _seen_mat.add(_mobj.path_id)
        for _ext_pid, _ext_obj in aP.items():
            if _ext_obj is not None and _ext_obj.type.name == 'Material' and _ext_obj.path_id not in _seen_mat:
                _fx_material_objs.append(_ext_obj); _seen_mat.add(_ext_obj.path_id)
        apply_fx_color(_fx_texture_objs, color_spec, _fx_material_objs, az)
    aS = {}
    bq = set()
    _next_unique_pid = None
    if unique_namespace:
        _existing_ids = [int(x) for x in aM.objects.keys() if isinstance(x, int) and x > 0]
        _next_unique_pid = (max(_existing_ids) + 1) if _existing_ids else 1
    def _alloc_clone_pid():
        nonlocal _next_unique_pid
        if _next_unique_pid is None:
            raise RuntimeError('clone pid allocator not initialized')
        while _next_unique_pid in aM.objects or _next_unique_pid in bq:
            _next_unique_pid += 1
        pid = _next_unique_pid
        bq.add(pid)
        _next_unique_pid += 1
        return pid
    for aa in sorted(aF):
        aS[0, aa] = _alloc_clone_pid() if unique_namespace else p(aM, aa, bq)
    for X in sorted(aP):
        aS[X] = _alloc_clone_pid() if unique_namespace else p(aM, X[1], bq)
    ba = c(bl)
    bm = {ah.path: W for W, ah in enumerate(ba.externals, start=1)}
    bs = {}
    for ax, aa in br.items():
        if ax in aT:
            continue
        if aa not in bm:
            ba.externals.append(f.copy(aL.externals[ax - 1]))
            bm[aa] = len(ba.externals)
            az('   + them external %s' % aa)
        bs[ax] = bm[aa]
    aY = {}
    for ab in list(aM.objects.values()):
        aY.setdefault(r(ab), ab)

    def bt(bx):
        return aY.get(r(bx))

    def bu(bD):
        bB = r(bD)
        for bx, by in enumerate(aM.types):
            bA = (getattr(by, 'class_id', None), getattr(by, 'script_id', None), getattr(by, 'old_type_hash', None))
            if bA == bB:
                return (bx, by)
        bC = bD.serialized_type
        if bC is None:
            return (None, None)
        bz = f.copy(bC)
        if hasattr(bC, 'nodes'):
            bz.nodes = f.deepcopy(bC.nodes)
        aM.types.append(bz)
        az('   + them SerializedType %s' % bD.type.name)
        return (len(aM.types) - 1, bz)
    bi = {(0, aa): aT[0][aa] for aa in aF if aa in aT[0]}
    bi.update(aP)
    bv = {}
    for (au, aC), Z in bi.items():
        aD = bytearray((P(Z) if Z.type.name == 'Texture2D' else None) or e(Z))
        ay = J(Z, aD, lambda bx, by: (bx, by) in aS)
        if ay is None:
            ay = list(u(bytes(aD), bh, lambda bx, by, bz: (bx, by) in aS))
        for aA, ai, am in ay:
            X = (ai, am)
            i.pack_into('<i', aD, aA, 0)
            i.pack_into('<q', aD, aA + 4, aS[X])
        if bs:
            at = J(Z, aD, lambda bx, by: bx in bs)
            if at is None:
                # Kieu khong doc duoc typetree (ParticleSystemRenderer, ParticleSystem,
                # Texture2D...) truoc day bi BO QUA buoc doi fileID external => PPtr toi
                # Material/Texture nam trong file _raw giu nguyen chi so external cua
                # NGUON, trong battleotherui chi so do tro di dau khac => mat material,
                # FX thieu manh. Dung chinh bo quet byte (chi tra ve vi tri da resolve
                # duoc sang object thuc) nen an toan.
                at = list(u(bytes(aD), bh, lambda bx, by, bz: bx in bs))
            for aA, ai, S in at:
                i.pack_into('<i', aD, aA, bs[ai])
        an = bt(Z)
        if an is None:
            aE, ap = bu(Z)
            if aE is None:
                az('   ! bo qua %s (khong dung duoc type)' % Z.type.name)
                continue
            an = next(iter(aM.objects.values()))
            Y = h(an)
            Y.type_id = aE
            Y.serialized_type = ap
            Y.class_id = Z.class_id
            Y.type = Z.type
            aY.setdefault(r(Z), Y)
        else:
            Y = h(an)
        Y.path_id = aS[au, aC]
        aM.objects[Y.path_id] = Y
        Y.set_raw_data(bytes(aD))
        bv[Y.path_id] = bytes(aD)
    be = [(X, aG) for X, aG in aS.items() if aG not in aM.objects]
    if be:
        aZ = ', '.join(('%s:%s->%s' % (bx[0], bx[1], bz) for bx, bz in be[:5]))
        raise t('FX thieu object sau khi copy: %s' % aZ)
    aV = []
    for X, bj in bi.items():
        bk = e(bj)
        bc = bv[aS[X]]
        ar = J(bj, bk, lambda bx, by: (bx, by) in aS)
        if ar is None:
            ar = u(bk, bh, lambda bx, by, bz: (bx, by) in aS)
        for aA, ai, am in ar:
            aN = aS[ai, am]
            if aA + 12 > len(bc):
                aV.append((X, aA, aN, 'short'))
                continue
            aQ = i.unpack_from('<i', bc, aA)[0]
            aR = i.unpack_from('<q', bc, aA + 4)[0]
            if aQ != 0 or aR != aN:
                aV.append((X, aA, aN, (aQ, aR)))
    if aV:
        X, aA, aN, aw = aV[0]
        raise t('FX PPtr remap loi tai %s:%s +0x%X, can %s, gap %s' % (X[0], X[1], aA, aN, aw))
    aX = aS[0, aW]
    av = aM.objects.get(aX)
    if av is None:
        raise t('transform FX khong duoc copy sang')
    U = d(aT[0][aW])
    if U is None:
        raise t('khong doc duoc transform FX o file nguon')
    # Tao raw Transform moi tu source, remap PPtr sang object clone, sau do
    # sua he quy chieu/parent.
    y(U, aS)
    U['m_Father'] = {'m_FileID': 0, 'm_PathID': G}
    U['m_LocalPosition'] = _source_pos
    U['m_LocalRotation'] = _source_rot
    if size_override is not None:
        _sc = float(size_override)
        U['m_LocalScale'] = {'x': _sc, 'y': _sc, 'z': _sc}
    else:
        U['m_LocalScale'] = _source_scale
    av.save_typetree(U)
    # v40 diagnostic: keep the original mount, target, mode and the two known bools.
    # The CButtonActiveEffect serialized payload has Color32 @40..43, then three
    # bool fields at @44/@48/@52, mode @56 and duration @60.  We tested @48/@52,
    # but @44 had not been isolated. Keep the no-cut condition from the successful
    # Infinity tests and flip only this previously-untried bool.
    try:
        import math as _math_v40
        _CBUTTON_GUID_v40 = bytes.fromhex('e8bd68567d92fbef09a107cd338c400b')
        _patched_v40 = 0
        for _obj_v40 in list(aM.objects.values()):
            if _obj_v40.type.name != 'MonoBehaviour':
                continue
            try:
                if bytes(_obj_v40.serialized_type.script_id) != _CBUTTON_GUID_v40:
                    continue
            except Exception:
                continue
            _raw_v40 = bytearray(e(_obj_v40))
            if len(_raw_v40) < 64:
                continue
            _raw_v40[44] = 1
            i.pack_into('<i', _raw_v40, 56, 20)
            i.pack_into('<f', _raw_v40, 60, 3)
            _obj_v40.set_raw_data(bytes(_raw_v40))
            _patched_v40 += 1
        az('   TEST FIX: CButtonActiveEffect bool@44=1, mode=20, duration=3 (%d patched)' % _patched_v40)
    except Exception as _ex_v40:
        az('   ! TEST v54 patch skipped: %s' % _ex_v40)
    # Tang SortingGroup ngay tren cac object clone cua layer nay.
    # Lam trong cung environment, khong save/reload bundle trung gian va khong
    # sua PPtr sau khi reload. Day la cach an toan hon cho multi-layer FX.
    _layer_step = 10000 * max(0, int(layer_index) - 1)
    if _layer_step:
        _sorted_count = 0
        for _clone_pid in aS.values():
            _clone_obj = R.get(_clone_pid)
            if _clone_obj is None or _clone_obj.type.name != 'SortingGroup':
                continue
            try:
                _sg = d(_clone_obj)
                if isinstance(_sg, dict) and 'm_SortingOrder' in _sg:
                    _sg['m_SortingOrder'] = int(_sg.get('m_SortingOrder', 0)) + _layer_step
                    _clone_obj.save_typetree(_sg)
                    _sorted_count += 1
            except Exception:
                pass
        az('   FX layer %d: sorting +%d (%d SortingGroup)' % (int(layer_index), _layer_step, _sorted_count))

    ag = R[G]
    af = d(ag)
    aB = [T['m_PathID'] for T in af['m_Children'] if T.get('m_PathID') != K]
    if mount_children is not None:
        if not append:
            mount_children[:] = [aX]
        else:
            mount_children.append(aX)
        _base_children = list(mount_children)
    elif append:
        _base_children = aB + [aX]
    else:
        _base_children = [aX]

    # Khi chon 0 = MẶC ĐỊNH, giu circle goc trong effect.
    # Dat no vao dung vi tri layer theo yeu cau.
    if keep_default and K in R:
        _children_ids = [pid for pid in _base_children if pid != K]
        _insert_at = max(0, min(len(_children_ids), int(default_layer) - 1))
        _children_ids.insert(_insert_at, K)
        _children = [{'m_FileID': 0, 'm_PathID': pid} for pid in _children_ids]
    else:
        _children = [{'m_FileID': 0, 'm_PathID': pid} for pid in _base_children]
    af['m_Children'] = _children
    ag.save_typetree(af)
    if not keep_default and K in R:
        ad = R[K]
        ac = d(ad)
        ac['m_Father'] = {'m_FileID': 0, 'm_PathID': 0}
        ac['m_Children'] = []
        ad.save_typetree(ac)
    az('   FX : %d object, mount %s%s' % (len(bi), av.type.name, ' (layer %d)' % layer_index if layer_count > 1 else ''))
    return len(bi)

def apply_default_layer_sorting(env, layer_index, az=lambda s: None):
    """Offset SortingGroup orders inside the original default circle layer."""
    if not layer_index or int(layer_index) <= 1:
        return
    try:
        root_obj = env.objects.get(K)
        if root_obj is None or root_obj.type.name not in ('Transform', 'RectTransform'):
            return
        delta = 10000 * (int(layer_index) - 1)
        stack = [K]
        seen = set()
        count = 0
        while stack:
            pid = stack.pop()
            if pid in seen or pid == 0:
                continue
            seen.add(pid)
            tr_obj = env.objects.get(pid)
            if tr_obj is None or tr_obj.type.name not in ('Transform', 'RectTransform'):
                continue
            tr = d(tr_obj)
            if not isinstance(tr, dict):
                continue
            go_pid = tr.get('m_GameObject', {}).get('m_PathID')
            go = env.objects.get(go_pid) if go_pid else None
            gd = d(go) if go is not None else None
            if isinstance(gd, dict):
                for comp in gd.get('m_Component', []):
                    cp = comp.get('component', {}).get('m_PathID')
                    co = env.objects.get(cp) if cp else None
                    if co is None or co.type.name != 'SortingGroup':
                        continue
                    ct = d(co)
                    if isinstance(ct, dict) and 'm_SortingOrder' in ct:
                        ct['m_SortingOrder'] = int(ct.get('m_SortingOrder', 0)) + delta
                        co.save_typetree(ct)
                        count += 1
            for ch in tr.get('m_Children', []):
                stack.append(ch.get('m_PathID'))
        az('   DEFAULT layer %d: sorting +%d (%d SortingGroup)' % (int(layer_index), delta, count))
    except Exception as ex:
        az('   ! DEFAULT sorting skipped: %s' % ex)


def apply_layer_sorting(env, layer_specs, az=lambda s: None):
    """Repair cloned FX component links after reload and apply layer render order."""
    if not layer_specs:
        return
    try:
        root_obj = next((o for o in env.objects if o.path_id == G and o.type.name in ('Transform', 'RectTransform')), None)
        if root_obj is None:
            return
        af = root_obj.assets_file
        root = d(root_obj)
        children = root.get('m_Children', []) if isinstance(root, dict) else []
        if len(children) < len(layer_specs):
            return

        # Owner map: component PathID -> GameObject PathID.
        owner = {}
        for obj in env.objects:
            if obj.type.name != 'GameObject':
                continue
            go = d(obj)
            if not isinstance(go, dict):
                continue
            for comp in go.get('m_Component', []):
                cp = comp.get('component', {}).get('m_PathID')
                if cp:
                    owner[cp] = obj.path_id

        for idx, spec in enumerate(layer_specs):
            delta = 10000 * max(0, int(spec.get('layer', idx + 1)) - 1)
            stack = [children[idx].get('m_PathID')]
            seen = set()
            repaired = 0
            sorted_count = 0
            while stack:
                pid = stack.pop()
                if pid in seen or pid == 0:
                    continue
                seen.add(pid)
                tr_obj = af.objects.get(pid)
                if tr_obj is None or tr_obj.type.name not in ('Transform', 'RectTransform'):
                    continue
                tr = d(tr_obj)
                if not isinstance(tr, dict):
                    continue
                go_pid = tr.get('m_GameObject', {}).get('m_PathID')
                real_go_pid = owner.get(tr_obj.path_id)
                if real_go_pid is not None and go_pid != real_go_pid:
                    tr['m_GameObject'] = {'m_FileID': 0, 'm_PathID': real_go_pid}
                    tr_obj.save_typetree(tr)
                    repaired += 1
                    go_pid = real_go_pid
                go_obj = af.objects.get(go_pid) if go_pid else None
                go = d(go_obj) if go_obj is not None else None
                if isinstance(go, dict):
                    for comp in go.get('m_Component', []):
                        cp = comp.get('component', {}).get('m_PathID')
                        co = af.objects.get(cp)
                        if co is None:
                            continue
                        ct = d(co)
                        if not isinstance(ct, dict):
                            continue
                        real_owner = owner.get(co.path_id, go_pid)
                        if 'm_GameObject' in ct and real_owner and ct.get('m_GameObject', {}).get('m_PathID') != real_owner:
                            ct['m_GameObject'] = {'m_FileID': 0, 'm_PathID': real_owner}
                            co.save_typetree(ct)
                            repaired += 1
                        if delta and 'm_SortingOrder' in ct:
                            ct['m_SortingOrder'] = int(ct.get('m_SortingOrder', 0)) + delta
                            co.save_typetree(ct)
                            sorted_count += 1
                for ch in tr.get('m_Children', []):
                    stack.append(ch.get('m_PathID'))
            az('   FX layer %d: repaired %d link, sorting +%d (%d object)' % (int(spec.get('layer', idx+1)), repaired, delta, sorted_count))
    except Exception as ex:
        az('   ! FX layer repair skipped: %s' % ex)


def P(Z):
    U = e(Z)
    R = Z.read()
    T = bytes(R.image_data)
    if not T:
        return None
    W = R.m_StreamData.path or ''
    if not W:
        return U
    X = len(W.encode('utf8'))
    Y = 8 + 4 + 4 + X
    Y += -X % 4
    S = 4 + Y
    V = U[:len(U) - S]
    return V + i.pack('<I', len(T)) + T + i.pack('<Q', 0) + i.pack('<I', 0) + i.pack('<I', 0)

def N(aC, aG, ax, an=lambda s: None):
    av = c(aC)
    S = av.objects
    ak, T = g(aG, ax, 'spr.assetbundle')
    R = {aa.path_id: aa for aa in ak.objects}
    az = {}
    for ap, aa in R.items():
        if aa.type.name != 'Sprite':
            continue
        V = d(aa)
        if V:
            az[V['m_Name']] = (ap, V)
    if not az:
        raise t('file sprite_raw khong co Sprite nao')
    au = {}
    for ap, aa in R.items():
        if aa.type.name != 'SpriteAtlas':
            continue
        ah = d(aa)
        if ah:
            for Y, ac in ah.get('m_RenderDataMap', []):
                au[tuple(Y['first'].values()), Y['second']] = ac
    aD = set()
    for at, (ap, V) in az.items():
        if at not in F:
            continue
        if V['m_SpriteAtlas']['m_PathID'] != 0:
            am = (tuple(V['m_RenderDataKey']['first'].values()), V['m_RenderDataKey']['second'])
            ag = au.get(am)
            if ag:
                aD.add(ag['texture']['m_PathID'])
        else:
            aD.add(V['m_RD']['texture']['m_PathID'])
    aD.discard(0)
    aF = next((aH for aH in aC.objects if aH.type.name == 'Texture2D'), None)
    aE = next((aH for aH in aC.objects if aH.type.name == 'Sprite'), None)
    if aF is None or aE is None:
        raise t('battleotherui thieu kieu Texture2D/Sprite')
    aB = {}
    for ai in sorted(aD):
        if ai not in R:
            continue
        af = P(R[ai])
        if af is None:
            continue
        ao = p(av, ai)
        Z = h(aF)
        Z.path_id = ao
        av.objects[ao] = Z
        Z.set_raw_data(af)
        aB[ai] = ao
    ay = {}
    for at in F:
        if at not in az:
            continue
        ap, V = az[at]
        if V['m_SpriteAtlas']['m_PathID'] != 0:
            am = (tuple(V['m_RenderDataKey']['first'].values()), V['m_RenderDataKey']['second'])
            ag = au.get(am)
            if ag is None:
                an('   ! %s: khong co trong RenderDataMap, bo qua' % at)
                continue
            for W in ('textureRect', 'textureRectOffset', 'atlasRectOffset', 'uvTransform', 'downscaleMultiplier', 'settingsRaw'):
                V['m_RD'][W] = ag[W]
            aA = ag['texture']['m_PathID']
        else:
            aA = V['m_RD']['texture']['m_PathID']
        if aA not in aB:
            an('   ! %s: thieu texture, bo qua' % at)
            continue
        V['m_SpriteAtlas'] = {'m_FileID': 0, 'm_PathID': 0}
        V['m_AtlasTags'] = []
        V['m_RD']['texture'] = {'m_FileID': 0, 'm_PathID': aB[aA]}
        V['m_RD']['alphaTexture'] = {'m_FileID': 0, 'm_PathID': 0}
        ao = p(av, ap)
        Z = h(aE)
        Z.path_id = ao
        av.objects[ao] = Z
        Z.save_typetree(V)
        ay[at] = ao
    ar = {l[Z]: ay[Z] for Z in ay if Z in l}
    al = 0
    for ae, at in O.items():
        if ae not in S or at not in ay:
            continue
        aq = e(S[ae])
        if len(aq) < 100 or i.unpack_from('<i', aq, 88)[0] != 0:
            continue
        U = bytearray(aq)
        i.pack_into('<q', U, 92, ay[at])
        S[ae].set_raw_data(bytes(U))
        al += 1
    for ap, aa in list(av.objects.items()):
        if aa is None or aa.type.name != 'MonoBehaviour':
            continue
        aq = e(aa)
        if len(aq) < 100:
            continue
        if i.unpack_from('<q', aq, 20)[0] != E:
            continue
        if i.unpack_from('<i', aq, 88)[0] != 0:
            continue
        aj = i.unpack_from('<q', aq, 92)[0]
        if aj not in ar:
            continue
        U = bytearray(aq)
        i.pack_into('<q', U, 92, ar[aj])
        aa.set_raw_data(bytes(U))
        al += 1
    for X in k:
        if X in S:
            V = d(S[X])
            if V is not None:
                V['m_IsActive'] = True
                S[X].save_typetree(V)
    if 'CustomJoyStick_RockingBg' in az:
        ad = az['CustomJoyStick_RockingBg'][1]['m_Rect']['width']
        aw = abs(ad - x / 2.0) < 0.5
        if w in S:
            U = bytearray(e(S[w]))
            U[12] = 1 if aw else 0
            S[w].set_raw_data(bytes(U))
        if s in S:
            U = bytearray(e(S[s]))
            if len(U) > 104:
                U[104] = 0 if aw else 1
            S[s].set_raw_data(bytes(U))
        an('   G1 : RockingBg %gpx -> mirror=%s' % (ad, 'ON' if aw else 'OFF'))
    if 'CustomJoyStick_RockingArrow' in az and o in S:
        ab = az['CustomJoyStick_RockingArrow'][1]['m_Rect']
        if abs(ab['width'] - A[0]) < 0.5 and abs(ab['height'] - A[1]) < 0.5:
            V = d(S[o])
            if V is not None:
                V['m_LocalScale'] = {'x': C, 'y': C, 'z': C}
                V['m_AnchoredPosition'] = {'x': z, 'y': 0.0}
                S[o].save_typetree(V)
                an('   G2 : arrow %gx%g -> scale %.2f / anchorX %g' % (ab['width'], ab['height'], C, z))
        else:
            an('   G2 : arrow %gx%g khac chuan -> khong bu' % (ab['width'], ab['height']))
    an('   JOY: %d sprite, %d texture, %d Image da tro lai' % (len(ay), len(aB), al))
    return (len(ay), al)

def build_one(skin_id, files, button_bundle, out_path, log=lambda s: None, step=lambda: None):
    with n.TemporaryDirectory() as U:
        V = a.path.join(U, 'base.assetbundle')
        L(button_bundle, V)
        step()
        S = j.load(V)
        step()
        if files.get('effect'):
            m(S, files['effect'], files.get('effect_raw'), U, log)
        step()
        if files.get('sprite_raw'):
            N(S, files['sprite_raw'], U, log)
        step()
        T = a.path.join(U, 'out_std.assetbundle')
        with open(T, 'wb') as R:
            R.write(S.file.save(packer='lzma'))
        step()
        a.makedirs(a.path.dirname(out_path), exist_ok=True)
        M(T, out_path)
        step()
    return a.path.getsize(out_path)
