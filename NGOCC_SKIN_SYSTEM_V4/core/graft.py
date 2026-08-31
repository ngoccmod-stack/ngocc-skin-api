# -*- coding: utf-8 -*-
"""
Bo dieu phoi (orchestrator).

Tool nay gop NGUYEN VEN hai loi da chay tot, khong viet lai logic:

  core/fx_engine.py   = loi FX cua QuanBeo   (mod full effect)
                        -> gop external cua file nguon vao battleotherui
                        -> inline Texture2D cua FX (khong con phu thuoc .resS)
  core/joy_engine.py  = loi JOY cua AovButton (mod full joystick)
                        -> 2 bo joystick + vien chieu + BorderIndicatorUp/Down
                        -> S2 atlas/standalone, S3 inline atlas, G1 mirror, G2 border

build_one() chi noi hai loi lai theo dung thu tu goc:
    decrypt -> FX -> JOY -> save(lzma) -> encrypt
"""
import os, shutil, tempfile

from .aovlib import UnityPy, decrypt_bundle, encrypt_bundle
from . import fx_engine
from . import joy_engine
from . import shop_engine

GraftError = joy_engine.GraftError

# giu nguyen ten cu de code ngoai (neu co) van goi duoc
graft_fx = fx_engine.m
graft_joystick = joy_engine.graft_joystick
graft_shop = shop_engine.graft_shop

# cac bundle phu se duoc mod them neu co mat trong Button/
SHOP_BUNDLES = ['battlecommon.assetbundle', 'battlecommon_raw.assetbundle']


def build_one(skin_id, files, button_bundle, out_path, log=lambda s: None,
              step=lambda: None, button_dir=None, out_dir=None, effect_layers=None, align_to_button=False):
    """Ghep 1 skin -> ghi file da ma hoa ra out_path. Tra ve kich thuoc file.

    button_dir / out_dir: neu truyen vao, tool se mod them icon shop trong
    battlecommon*.assetbundle va ghi canh battleotherui.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, 'base.assetbundle')
        decrypt_bundle(button_bundle, base)
        step()

        env = UnityPy.load(base)
        step()

        # ---- FX ----
        _fx_specs = effect_layers
        if not _fx_specs and files.get('effect'):
            _fx_specs = [{'effect': files['effect'], 'effect_raw': files.get('effect_raw'),
                          'id': str(skin_id), 'name': '', 'hero': '', 'layer': 1, 'size': None, 'default': False}]

        if _fx_specs:
            _fx_specs = list(_fx_specs)
            _default_specs = [sp for sp in _fx_specs if sp.get('default') or sp.get('id') == '0']
            # The skin being modded onto the button is the trusted positional reference.
            # Its source FX is known to line up correctly; additional FX are expressed as
            # offsets relative to this anchor.
            _reference_anchor = None
            if align_to_button and files.get('effect'):
                try:
                    _reference_anchor = fx_engine.get_fx_anchor(files['effect'], tmp)
                    rp = _reference_anchor.get('position', {})
                    log('   ALIGN REF: %s position=(%.6g, %.6g, %.6g)' % (
                        str(skin_id), float(rp.get('x', 0.0)), float(rp.get('y', 0.0)), float(rp.get('z', 0.0))))
                except Exception as _align_ex:
                    log('   ! ALIGN REF skipped: %s' % _align_ex)
            _keep_default = bool(_default_specs)
            _default_layer = int(_default_specs[0].get('layer', 1)) if _default_specs else 1

            # FX phai duoc graft theo thu tu layer de root children nam dung thu tu.
            _ordered_fx_specs = sorted([sp for sp in _fx_specs if not (sp.get('default') or sp.get('id') == '0')],
                                       key=lambda sp: int(sp.get('layer', 1)))
            _fx_mount_children = []
            if _keep_default:
                fx_engine.apply_default_layer_sorting(env, _default_layer, log)

            for idx, spec in enumerate(_ordered_fx_specs, 1):
                _effect_path = spec['effect']
                _effect_raw_path = spec.get('effect_raw')
                # IMPORTANT: color is preprocessed on the standalone EFFECT bundle first,
                # using the same UnityPy_AOV + PIL -> RGBA32 workflow as the working Texture2D tool.
                # This keeps Sprite/JOY untouched and avoids the Button Tool's limited decoder.
                if spec.get('color') and not spec.get('color', {}).get('keep'):
                    _effect_path, _effect_raw_path = fx_engine.preprocess_effect_color(
                        _effect_path, _effect_raw_path, tmp, spec.get('color'), log)
                fx_engine.m(env, _effect_path, _effect_raw_path, tmp, log,
                            append=(idx > 1),
                            size_override=spec.get('size'),
                            layer_index=spec.get('layer', idx),
                            layer_count=len(_fx_specs),
                            mount_children=_fx_mount_children,
                            unique_namespace=(len(_ordered_fx_specs) > 1),
                            keep_default=_keep_default,
                            default_layer=_default_layer,
                            reference_anchor=_reference_anchor,
                            is_reference_fx=(str(spec.get('id')) == str(skin_id)),
                            color_spec=None)

            # Chi chon 0 = MẶC ĐỊNH thi giu nguyen circle goc; khong can graft FX moi.
            if _keep_default and not _ordered_fx_specs:
                log('   FX: giữ nguyên hiệu ứng MẶC ĐỊNH')
        elif files.get('effect'):
            fx_engine.m(env, files['effect'], files.get('effect_raw'), tmp, log)
        step()
        # ---- JOYSTICK: loi AovButton, nguyen ven ----
        if files.get('sprite_raw'):
            joy_engine.graft_joystick(env, files['sprite_raw'], tmp, log)
        step()

        std = os.path.join(tmp, 'out_std.assetbundle')
        with open(std, 'wb') as f:
            f.write(env.file.save(packer='lzma'))
        step()

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        encrypt_bundle(std, out_path)
        step()

        # ---- SHOP: ghi de tai cho trong battlecommon* (neu co file) ----
        if button_dir and out_dir and files.get('sprite_raw'):
            for i, name in enumerate(SHOP_BUNDLES):
                src = os.path.join(button_dir, name)
                if not os.path.isfile(src):
                    continue
                try:
                    n = shop_engine.graft_shop(src, files['sprite_raw'],
                                               os.path.join(out_dir, name),
                                               tmp, log, tag=str(i))
                    if n == 0:
                        shutil.copy2(src, os.path.join(out_dir, name))
                except Exception as e:
                    log('   ! SHOP %s: %s — copy nguyen ban' % (name, e))
                    try:
                        shutil.copy2(src, os.path.join(out_dir, name))
                    except Exception:
                        pass
        step()
    return os.path.getsize(out_path)
