#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOV Button & Banner Modder — phien vo han
Cau truc:
  Source/   personalbuttoneffect_<ID>[_raw].assetbundle , personalbuttonsprite_<ID>_raw.assetbundle
  Button/   battleotherui.assetbundle , battleotherui_raw.assetbundle   (chua mod)
  Skin/     skin.txt
  lib/      UnityPy/ , Protect.py
  Output/   <ID>/Resources/1.63.1/assetbundle/uisystem/battle/battleotherui.assetbundle
"""
import os, sys, time, shutil, traceback, re, json, copy

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from core import ui
from core.skinlist import build_menu
from core import graft
from core import fx_engine

SRC_DIR = os.path.join(ROOT, 'Source')
BTN_DIR = os.path.join(ROOT, 'Button')
SKN_DIR = os.path.join(ROOT, 'Skin')
OUT_DIR = os.path.join(ROOT, 'Output')
PRESET_DIR = os.path.join(ROOT, 'FX_Presets')

OUT_REL = os.path.join('Resources', '1.63.1', 'assetbundle', 'uisystem', 'battle')
STEPS   = 7          # so buoc trong build_one


def preflight():
    miss = []
    btn = os.path.join(BTN_DIR, 'battleotherui.assetbundle')
    skn = os.path.join(SKN_DIR, 'skin.txt')
    if not os.path.isfile(btn):
        miss.append('Button/battleotherui.assetbundle')
    if not os.path.isfile(skn):
        miss.append('Skin/skin.txt')
    if not os.path.isdir(SRC_DIR):
        miss.append('Source/')
    if miss:
        ui.err('[X] Thieu:')
        for m in miss:
            print('     - ' + m)
        print()
        ui.info('Tao du cau truc thu muc roi chay lai.')
        sys.exit(1)
    return btn, skn


def show_menu(rows):
    w = ui.width()
    print()
    print(ui.B + ' DANH SACH BUTTON CO THE MOD' + ui.R
          + ui.DIM + '   (%d muc)' % len(rows) + ui.R)
    ui.rule()

    n_w = len(str(len(rows)))
    # be ngang con lai cho ten = tong - (so tt + ID + nhan + khoang trang)
    name_w = max(22, w - (2 + n_w + 2 + 7 + 10))

    for i, r in enumerate(rows, 1):
        hero = (r['hero'] or '').strip()
        skin = r['name'].strip()
        full = ('%s %s' % (hero, skin)).strip() if hero else skin
        if len(full) > name_w:
            full = full[:name_w - 1] + '\u2026'
            hero_show = full[:len(hero)] if len(hero) <= len(full) else full
        else:
            hero_show = hero
        # to mau phan ten tuong, phan con lai in dam
        if hero_show and full.startswith(hero_show):
            label = ui.YL + hero_show + ui.R + ui.B + full[len(hero_show):] + ui.R
        else:
            label = ui.B + full + ui.R
        pad = ' ' * max(0, name_w - len(full))
        print(' %s%*d.%s %s%-6s%s %s%s %s[%s]%s'
              % (ui.DIM, n_w, i, ui.R,
                 ui.CY, r['id'], ui.R,
                 label, pad,
                 ui.DIM, r['parts'], ui.R))
    ui.rule()
    ui.info('  Nhap duoc CA so thu tu lan ID   ·   FX = hieu ung nut danh, JOY = joystick')


def parse_ids(text, rows):
    by_id = {r['id']: r for r in rows}
    picked, bad = [], []
    for tok in text.replace(',', ' ').split():
        tok = tok.strip()
        if not tok:
            continue
        if tok.isdigit() and tok in by_id:
            if by_id[tok] not in picked:
                picked.append(by_id[tok])
        elif tok.isdigit() and 1 <= int(tok) <= len(rows):
            r = rows[int(tok) - 1]
            if r not in picked:
                picked.append(r)
        else:
            bad.append(tok)
    return picked, bad


def show_fx_menu(rows):
    fx_rows = [r for r in rows if r['files'].get('effect')]
    print()
    print(ui.B + ' DANH SACH EFFECT BUTTON CO THE CHON' + ui.DIM + '   (%d muc)' % len(fx_rows) + ui.R)
    ui.rule()
    print(' %s0.%s %sMẶC ĐỊNH%s' % (ui.CY + ui.B, ui.R, ui.YL, ui.R))
    n_w = len(str(len(fx_rows)))
    w = ui.width()
    name_w = max(22, w - (2 + n_w + 2 + 7 + 6))
    for i, r in enumerate(fx_rows, 1):
        hero = (r['hero'] or '').strip()
        skin = r['name'].strip()
        full = ('%s %s' % (hero, skin)).strip() if hero else skin
        if len(full) > name_w:
            full = full[:name_w - 1] + '…'
        prefix = ui.CY + ui.B + (' %*d. ID %-6s' % (n_w, i, r['id'])) + ui.R
        label = ui.YL + (' ' + full if full else '') + ui.R
        print(prefix + label)
    ui.rule()
    ui.info('  Nhap duoc so thu tu, ID, 0 = MẶC ĐỊNH; nhieu cai cach nhau bang dau phay')
    return fx_rows


def strict_pick_fx(text, fx_rows):
    by_id = {r['id']: r for r in fx_rows}
    picked, bad = [], []
    default_spec = {'default': True, 'id': '0', 'hero': '', 'name': 'MẶC ĐỊNH',
                    'files': {'effect': None, 'effect_raw': None}}
    for tok in text.replace(',', ' ').split():
        tok = tok.strip()
        if not tok.isdigit():
            bad.append(tok); continue
        if tok == '0':
            if default_spec not in picked:
                picked.append(default_spec)
            continue
        if tok in by_id:
            r = by_id[tok]
        elif 1 <= int(tok) <= len(fx_rows):
            r = fx_rows[int(tok)-1]
        else:
            bad.append(tok); continue
        if r not in picked:
            picked.append(r)
    return picked, bad

def ask_yes_no(prompt):
    while True:
        try:
            v = input(ui.B + prompt + ui.R + ' ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None
        if v in ('y', 'n'):
            return v
        ui.err('Sai cú pháp. Vui lòng chọn lại')


def ask_positive_size(row):
    try:
        original = fx_engine.get_fx_size(row['files']['effect'], row['files'].get('effect_raw'))
    except Exception:
        original = 1.0
    while True:
        _hero = (row.get('hero') or '').strip()
        _skin_label = ('%s %s' % (_hero, row['name'])).strip() if _hero else row['name']
        try:
            raw = input(ui.B + ' Size gốc của nút bấm %s - %s là %.6g. Bạn muốn chỉnh thành ? :' % (ui.CY + ui.B + str(row.get('id','')) + ui.R, ui.YL + _skin_label + ui.R, original) + ui.R + ' ').strip()
        except (EOFError, KeyboardInterrupt):
            return None
        # Chi chap nhan so thuc don gian, khong chu/cac ky tu la/NaN/Infinity.
        if not re.fullmatch(r'(?:\d+(?:\.\d+)?|\.\d+)', raw):
            ui.err('Sai cú pháp. Vui lòng chọn lại!')
            continue
        try:
            value = float(raw)
        except Exception:
            ui.err('Sai cú pháp. Vui lòng chọn lại!')
            continue
        if value <= 0:
            ui.err('Sai cú pháp. Vui lòng chọn lại!')
            continue
        return value




def _boxed_menu(title, items):
    w=max(50,ui.width())
    inner=w-2
    print(ui.CY+ui.B+'╔'+'═'*inner+'╗'+ui.R)
    print(ui.CY+ui.B+'║'+title.center(inner)+'║'+ui.R)
    print(ui.CY+ui.B+'╠'+'═'*inner+'╣'+ui.R)
    for text in items:
        line='  '+text
        if len(line)>inner: line=line[:inner]
        print(ui.CY+'║'+ui.R+line.ljust(inner)+ui.CY+'║'+ui.R)
    print(ui.CY+ui.B+'╚'+'═'*inner+'╝'+ui.R)

def configure_effects(rows, initial_picked):
    """Menu FX độc lập: chọn nhiều tính năng một lần, mỗi tính năng xử lý theo từng FX."""
    ans = ask_yes_no('Có muốn điều chỉnh hiệu ứng bấm riêng? Y/N')
    if ans is None or ans == 'n':
        return None

    _boxed_menu('ĐIỀU CHỈNH HIỆU ỨNG BẤM', [
        ' 1. Đè nhiều hiệu ứng bấm',
        ' 2. Nhân bản hiệu ứng bấm',
        ' 3. Điều chỉnh Size hiệu ứng bấm',
        ' 4. Fix lệch theo hiệu ứng gốc',
        ' 5. Chỉnh vị trí riêng',
        ' 6. Xoay hiệu ứng',
        ' 7. Chỉnh màu hiệu ứng',
        ' 8. Lưu / dùng cấu hình',
        ' 9. Điều chỉnh độ trong suốt',
        '10. Chỉnh kích thước Ngang / Thẳng',
        '11. Điều chỉnh độ sáng hiệu ứng',
        '12. Chỉnh thứ tự hiển thị',
        '13. Sao chép cài đặt từ hiệu ứng khác',
        '14. Khôi phục cài đặt gốc',
        '15. Đảo chiều xoay hiệu ứng',
        ' 0. Thoát',
    ])
    allowed=set(range(1,16))
    while True:
        try:
            raw=input(ui.B+' Chọn tính năng (nhiều cái cách nhau bằng dấu phẩy): '+ui.R).strip()
        except (EOFError, KeyboardInterrupt):
            return None
        vals=[]; bad=False
        for tok in raw.replace(' ',',').split(','):
            tok=tok.strip()
            if not tok: continue
            if tok == '0':
                return False
            if not tok.isdigit() or int(tok) not in allowed:
                bad=True; break
            tok=str(int(tok))
            if tok not in vals: vals.append(tok)
        if vals and not bad:
            break
        ui.err('Sai cú pháp. Vui lòng chọn lại')

    use_multi='1' in vals
    use_clone='2' in vals
    use_size='3' in vals
    use_align='4' in vals
    use_position='5' in vals
    use_rotation='6' in vals
    use_color='7' in vals
    use_preset='8' in vals
    use_opacity='9' in vals
    use_scale_xy='10' in vals
    use_brightness='11' in vals
    use_order='12' in vals
    use_copy='13' in vals
    use_restore='14' in vals
    use_reverse_rotation='15' in vals

    # Chỉ chức năng 1 mới gọi lại danh sách FX.
    if use_multi:
        fx_rows=show_fx_menu(rows)
        while True:
            try: raw=input(ui.B+' Chọn Skin FX (số thứ tự hoặc ID, nhiều cái cách nhau bằng dấu phẩy): '+ui.R).strip()
            except (EOFError, KeyboardInterrupt): return None
            picked,bad=strict_pick_fx(raw,fx_rows)
            if bad or not picked:
                ui.err('Sai cú pháp. Vui lòng chọn lại'); continue
            break
    else:
        picked=[dict(r) for r in initial_picked]

    n=len(picked); specs=[]; used_layers=set()
    for idx,row in enumerate(picked,1):
        is_default=bool(row.get('default')); layer=1
        if use_multi and n>1:
            _hero=(row.get('hero') or '').strip()
            if is_default:
                head=ui.CY+('Skin số %d - ID 0'%idx)+ui.R+' - '+ui.YL+'MẶC ĐỊNH'+ui.R
            else:
                label=(('%s %s'%(_hero,row['name'])).strip() if _hero else row['name'])
                head=ui.CY+('Skin số %d - ID %s'%(idx,row['id']))+ui.R+' - '+ui.YL+label+ui.R
            while True:
                print(head+' nằm ở ?')
                for lv0 in range(1,n+1): print('%d. Lớp %d'%(lv0,lv0))
                print(ui.DIM+'(Lớp thấp nhất sẽ nằm dưới cùng.)'+ui.R)
                lv=input(ui.B+' Chọn lớp: '+ui.R).strip()
                if not lv.isdigit() or not (1<=int(lv)<=n) or int(lv) in used_layers:
                    ui.err('Sai cú pháp. Vui lòng chọn lại'); continue
                layer=int(lv); used_layers.add(layer); break
        else:
            used_layers.add(layer)
        specs.append({'effect':row['files'].get('effect') if not is_default else None,
                      'effect_raw':row['files'].get('effect_raw') if not is_default else None,
                      'id':row.get('id','0'),'source_id':row.get('id','0'),'name':row.get('name',''),'hero':row.get('hero',''),
                      'layer':layer,'size':None,'default':is_default,'clone_index':0,'clone_of_id':row.get('id','0')})

    return {'specs':specs,'align_to_button':bool(use_align),'use_align':use_align,'use_position':use_position,
            'use_rotation':use_rotation,'use_color':use_color,'use_preset':use_preset,
            'use_opacity':use_opacity,'use_scale_xy':use_scale_xy,'use_brightness':use_brightness,
            'use_order':use_order,'use_copy':use_copy,'use_restore':use_restore,
            'use_reverse_rotation':use_reverse_rotation,'use_clone':use_clone,
            'use_size':use_size,'initial_picked':initial_picked,'selected_menu':vals}



def configure_clone_selected(effect_layers):
    """Nhân bản một hoặc nhiều FX đang có thành các instance độc lập.

    Clone giữ nguyên toàn bộ cấu hình tại thời điểm nhân bản, nhưng có ID riêng dạng
    <source_id>_01, <source_id>_02... để các bước chỉnh phía sau xử lý độc lập.
    """
    candidates=[i for i,sp in enumerate(effect_layers,1)
                if not sp.get('default') and sp.get('effect')]
    if not candidates:
        ui.warn('Không có FX để nhân bản.')
        return effect_layers

    print()
    print(ui.B+' CHỌN FX MUỐN NHÂN BẢN'+ui.R)
    ui.rule()
    for i,sp in enumerate(effect_layers,1):
        if i in candidates:
            print(' %s%2d.%s %s' % (ui.CY,i,ui.R,_row_label(sp)))
    ui.rule()
    while True:
        raw=input(ui.B+' Chọn FX muốn nhân bản (nhiều cái bằng dấu phẩy, e = thoát): '+ui.R).strip().lower()
        if raw=='e':
            return effect_layers
        vals=_parse_multi_int(raw,len(effect_layers))
        if vals:
            vals=[v for v in vals if v in candidates]
        if not vals:
            ui.err('Sai cú pháp. Vui lòng chọn lại')
            continue
        break

    out=[copy.deepcopy(sp) for sp in effect_layers]
    # Tính clone index tiếp theo theo source_id, không phụ thuộc thứ tự layer.
    next_index={}
    for sp in out:
        sid=str(sp.get('source_id') or sp.get('id',''))
        ci=int(sp.get('clone_index',0) or 0)
        if ci>next_index.get(sid,0):
            next_index[sid]=ci

    for idx in vals:
        base=out[idx-1]
        source_id=str(base.get('source_id') or base.get('id',''))
        current_max=next_index.get(source_id,0)
        while True:
            raw_count=input(ui.B+' Muốn tạo bao nhiêu clone cho %s? (0 = bỏ qua): '%_row_label(base)).strip().lower()
            if raw_count=='e':
                return effect_layers
            if not raw_count.isdigit():
                ui.err('Sai cú pháp. Vui lòng nhập số 0 trở lên hoặc e.')
                continue
            count=int(raw_count)
            break
        for _ in range(count):
            current_max += 1
            clone=copy.deepcopy(base)
            clone['source_id']=source_id
            clone['clone_index']=current_max
            clone['clone_of_id']=str(base.get('id',source_id))
            clone['id']=f'{source_id}_{current_max:02d}'
            # Giữ cùng source name/hero; _row_label sẽ hiển thị ID clone riêng.
            out.append(clone)
        next_index[source_id]=current_max
        if count:
            ui.info('  → %s: thêm %d clone.' % (_row_label(base),count))

    return out


def _row_label(row):
    hero=(row.get('hero') or '').strip(); skin=(row.get('name') or '').strip()
    full=(hero+' '+skin).strip() if hero else skin
    return ui.CY+ui.B+str(row.get('id',''))+ui.R+' - '+ui.YL+full+ui.R


def _effective_position(row, anchor_row=None, align_to_button=False):
    """Position currently used by graft, shown in friendly Ngang/Thẳng terms."""
    tr = fx_engine.get_fx_transform(row['files']['effect'], row['files'].get('effect_raw'))
    pos = dict(tr.get('position') or {})
    if align_to_button and anchor_row and str(row.get('id')) != str(anchor_row.get('id')):
        ref = fx_engine.get_fx_anchor(anchor_row['files']['effect'])
        rp = ref.get('position') or {}
        pos['x'] = float(pos.get('x',0.0)) - float(rp.get('x',0.0))
        pos['y'] = float(pos.get('y',0.0)) - float(rp.get('y',0.0))
        pos['z'] = float(pos.get('z',0.0)) - float(rp.get('z',0.0))
    return pos, float(tr.get('rotation_z', 0.0))


def _ask_number_or_skip(prompt, allow_negative=True):
    pat = r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)' if allow_negative else r'(?:\d+(?:\.\d+)?|\.\d+)'
    while True:
        raw=input(ui.B+prompt+' (e = bỏ qua): '+ui.R+' ').strip().lower()
        if raw=='e':
            return None
        if not re.fullmatch(pat, raw):
            ui.err('Sai cú pháp. Vui lòng nhập số hoặc e để bỏ qua!')
            continue
        try:
            return float(raw)
        except Exception:
            ui.err('Sai cú pháp. Vui lòng nhập số hoặc e để bỏ qua!')

def _ask_number(prompt, allow_negative=True):
    pat = r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)' if allow_negative else r'(?:\d+(?:\.\d+)?|\.\d+)'
    while True:
        raw=input(ui.B+prompt+ui.R+' ').strip()
        if not re.fullmatch(pat, raw):
            ui.err('Sai cú pháp. Vui lòng chọn lại!')
            continue
        try:
            return float(raw)
        except Exception:
            ui.err('Sai cú pháp. Vui lòng chọn lại!')


def configure_position_and_rotation(specs, initial_picked, align_to_button):
    """New 3-feature menu: position, rotation, save/use preset."""
    if not specs:
        return specs
    rows_by_id={str(r['id']):r for r in initial_picked}
    while True:
        print()
        _boxed_menu('ĐIỀU CHỈNH THÊM', [
            '1. Chỉnh vị trí riêng',
            '2. Xoay hiệu ứng',
            '3. Lưu / dùng cấu hình',
            '0. Bỏ qua',
        ])
        raw=input(ui.B+' Chọn (có thể nhập 1,2,3): '+ui.R).strip()
        if raw=='0': return specs
        vals=[]; bad=False
        for tok in raw.replace(' ', ',').split(','):
            tok=tok.strip()
            if not tok: continue
            if not tok.isdigit() or tok not in ('1','2','3'):
                bad=True; break
            if tok not in vals: vals.append(tok)
        if bad or not vals:
            ui.err('Sai cú pháp. Vui lòng chọn lại')
            continue

        if '1' in vals:
            for sp in specs:
                if sp.get('default') or not sp.get('effect'):
                    continue
                row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
                     'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
                anchor_row = rows_by_id.get(str(initial_picked[0].get('id'))) if initial_picked else None
                try:
                    pos,_ = _effective_position(row, anchor_row, align_to_button)
                except Exception:
                    pos={'x':0.0,'y':0.0,'z':0.0}
                print(); print(ui.B+' Vị trí hiện tại của '+_row_label(row)+ui.R)
                print('  Ngang : %.6g' % float(pos.get('x',0.0)))
                print('  Thẳng : %.6g' % float(pos.get('y',0.0)))
                print(ui.DIM+'  (+ Ngang = sang phải, - Ngang = sang trái)' + ui.R)
                print(ui.DIM+'  (+ Thẳng = lên trên, - Thẳng = xuống dưới)' + ui.R)
                dx=_ask_number_or_skip('Muốn dịch Ngang bao nhiêu? (+ phải / - trái)')
                dy=_ask_number_or_skip('Muốn dịch Thẳng bao nhiêu? (+ lên / - xuống)')
                dz=_ask_number_or_skip('Muốn dịch Pos Z bao nhiêu? (+ trước / - sau)')
                x=float(pos.get('x',0.0)) if dx is None else float(pos.get('x',0.0))+dx
                y=float(pos.get('y',0.0)) if dy is None else float(pos.get('y',0.0))+dy
                z=float(pos.get('z',0.0)) if dz is None else float(pos.get('z',0.0))+dz
                sp['position_override']={'x':x,'y':y,'z':z}
                ui.info('  → Vị trí mới: Ngang %.6g · Thẳng %.6g · Pos Z %.6g' % (sp['position_override']['x'], sp['position_override']['y'], sp['position_override']['z']))

        if '2' in vals:
            for sp in specs:
                if sp.get('default') or not sp.get('effect'):
                    continue
                row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
                     'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
                try:
                    _,rz=_effective_position(row, None, False)
                except Exception:
                    rz=0.0
                print(); print(ui.B+' Góc xoay hiện tại của '+_row_label(row)+': %.6g°'%rz+ui.R)
                print(ui.DIM+'  Nhập 62 = 62° · số âm = xoay ngược chiều' + ui.R)
                sp['rotation_z_override']=_ask_number('Muốn xoay thành bao nhiêu độ?')
                ui.info('  → Góc xoay mới: %.6g°' % sp['rotation_z_override'])

        # Chức năng 3 luôn chạy sau khi đã chỉnh vị trí/xoay, để khi lưu có đủ thông tin.
        if '3' in vals:
            _preset_result = preset_menu(specs, initial_picked, align_to_button)
            if _preset_result is None:
                return None
            specs, align_to_button = _preset_result
        break
    return specs


def _preset_safe_name(name):
    name=name.strip()
    if not name: return None
    if not re.fullmatch(r'[\w\-. ]+', name, re.UNICODE): return None
    return name


def _preset_payload(specs, initial_picked, align_to_button):
    clean=[]
    for sp in specs:
        c={k:sp.get(k) for k in ('id','source_id','name','hero','layer','size','default','clone_index','clone_of_id','position_override','rotation_z_override','disabled_textures','disabled_parts','opacity','scale_xy_override','brightness','part_scale_overrides','reverse_rotation')}
        # Keep color settings that are independent of unstable path IDs.
        if sp.get('color'):
            col=dict(sp['color'])
            col.pop('texture_keys', None)
            c['color']=col
        clean.append(c)
    return {'version':1,'button_ids':[r['id'] for r in initial_picked],
            'align_to_button':bool(align_to_button),'effects':clean}


def _load_preset_files(button_id=None):
    os.makedirs(PRESET_DIR, exist_ok=True)
    items=[]
    for fn in sorted(os.listdir(PRESET_DIR)):
        if not fn.lower().endswith('.json'): continue
        path=os.path.join(PRESET_DIR,fn)
        try:
            data=json.load(open(path,'r',encoding='utf-8'))
            if button_id and button_id not in [str(x) for x in data.get('button_ids',[])]:
                continue
            items.append((fn,path,data))
        except Exception:
            continue
    return items


def preset_menu(specs, initial_picked, align_to_button):
    while True:
        print(); print(ui.B+' CẤU HÌNH ĐÃ LƯU'+ui.R); ui.rule()
        print('  1. Lưu cấu hình hiện tại')
        print('  2. Dùng cấu hình đã lưu')
        print('  0. Quay lại')
        ui.rule()
        raw=input(ui.B+' Chọn: '+ui.R).strip()
        if raw=='0': return specs, align_to_button
        if raw=='1':
            while True:
                name=input(ui.B+' Nhập tên cấu hình: '+ui.R).strip()
                safe=_preset_safe_name(name)
                if not safe:
                    ui.err('Sai cú pháp. Tên chỉ nên gồm chữ, số, khoảng trắng, _ hoặc -.'); continue
                os.makedirs(PRESET_DIR, exist_ok=True)
                path=os.path.join(PRESET_DIR,safe+'.json')
                with open(path,'w',encoding='utf-8') as f:
                    json.dump(_preset_payload(specs,initial_picked,align_to_button),f,ensure_ascii=False,indent=2)
                ui.ok('Đã lưu cấu hình: FX_Presets/%s.json' % (safe,))
                return specs, align_to_button
        if raw=='2':
            items=_load_preset_files(str(initial_picked[0]['id']) if initial_picked else None)
            if not items:
                ui.warn('Chưa có cấu hình đã lưu cho ID này.')
                continue
            for i,(fn,_,data) in enumerate(items,1):
                print(' %s%2d.%s %s' % (ui.CY,i,ui.R,fn[:-5]))
            ui.rule()
            pick=input(ui.B+' Chọn cấu hình: '+ui.R).strip()
            if not pick.isdigit() or not (1<=int(pick)<=len(items)):
                ui.err('Sai cú pháp. Vui lòng chọn lại'); continue
            data=items[int(pick)-1][2]
            rowmap={str(r['id']):r for r in initial_picked}
            new=[]
            for saved in data.get('effects',[]):
                sid=str(saved.get('id',''))
                source_id=str(saved.get('source_id') or sid.split('_',1)[0])
                # Re-resolve source file by source ID; clone IDs such as 15015_01
                # point back to the original FX asset 15015.
                found=None
                for r in initial_picked:
                    if str(r['id'])==source_id: found=r; break
                if found is None:
                    found=globals().get('_CURRENT_ROWS_BY_ID',{}).get(source_id)
                if not found and saved.get('default'):
                    new.append({'default':True,'id':'0','hero':'','name':'MẶC ĐỊNH','files':{'effect':None,'effect_raw':None},
                                'layer':saved.get('layer',1),'size':None,'clone_index':1,'clone_of_id':'0'})
                    continue
                if not found:
                    continue
                sp={'id':sid,'source_id':source_id,'name':found['name'],'hero':found.get('hero',''),'files':found['files'],
                    'layer':saved.get('layer',1),'size':saved.get('size'),'default':False,
                    'clone_index':int(saved.get('clone_index',0) or 0),
                    'clone_of_id':str(saved.get('clone_of_id',source_id))}
                for k in ('position_override','rotation_z_override','disabled_textures','disabled_parts','opacity','scale_xy_override','brightness','part_scale_overrides','color','reverse_rotation'):
                    if k in saved: sp[k]=saved[k]
                new.append(sp)
            if new:
                ui.ok('Đã nạp cấu hình đã lưu.')
                return new, bool(data.get('align_to_button', align_to_button))
            ui.warn('Cấu hình không còn tìm thấy các ID nguồn hiện tại.')
            continue
        ui.err('Sai cú pháp. Vui lòng chọn lại')


def _color_label(row):
    hero=(row.get('hero') or '').strip(); skin=(row.get('name') or '').strip(); full=(hero+' '+skin).strip() if hero else skin
    return ui.CY+ui.B+str(row.get('id',''))+ui.R+' - '+ui.YL+full+ui.R

def _plain_color_label(row):
    hero=(row.get('hero') or '').strip(); skin=(row.get('name') or '').strip(); return (hero+' '+skin).strip() if hero else skin

def _parse_multi_int(raw,max_value):
    vals=[]
    for tok in re.split(r'[ ,]+',raw.strip()):
        if not tok or not tok.isdigit(): return None
        v=int(tok)
        if not 1<=v<=max_value: return None
        if v not in vals: vals.append(v)
    return vals or None

def show_color_palette():
    p=fx_engine.FX_COLOR_PALETTE; print(); print(ui.B+' BẢNG MÀU'+ui.DIM+'   (%d màu)'%len(p)+ui.R); ui.rule()
    for st in range(0,len(p),2):
        parts=[]
        for j in range(st,min(st+2,len(p))):
            nm,hx=p[j]; parts.append('%s%2d.%s %-18s %s%s%s'%(ui.CY,j+1,ui.R,nm,ui.DIM,hx,ui.R))
        print('    '.join(parts))
    print(' %s0.%s Nhập mã HEX riêng'%(ui.CY+ui.B,ui.R)); ui.rule()

def ask_palette_rgb():
    p=fx_engine.FX_COLOR_PALETTE
    while True:
        show_color_palette(); raw=input(ui.B+' Chọn màu: '+ui.R).strip()
        if raw=='0':
            hx=input(ui.B+' Nhập HEX (ví dụ FF4FA3): '+ui.R).strip()
            if re.fullmatch(r'[0-9a-fA-F]{6}',hx): return tuple(int(hx[k:k+2],16) for k in (0,2,4))
            ui.err('Sai cú pháp. Vui lòng chọn lại!'); continue
        if raw.isdigit() and 1<=int(raw)<=len(p):
            hx=p[int(raw)-1][1].lstrip('#'); return tuple(int(hx[k:k+2],16) for k in (0,2,4))
        ui.err('Sai cú pháp. Vui lòng chọn lại!')

def _fmt_hue(h): return '%d°'%(int(round(float(h)*360))%360)

def ask_texture_scope(row):
    try:
        catalog=fx_engine.scan_fx_texture_catalog_aov(row['files']['effect'],row['files'].get('effect_raw'))
    except Exception:
        catalog=[]
    # Pixel scan may be empty when every source texture is ETC/ASTC. Still list all
    # Texture2D objects by metadata so the user can target them; actual recoloring
    # falls back to the FX Material tint path.
    if not catalog or not any(it.get('hues') for it in catalog):
        try:
            raw_catalog=fx_engine.scan_fx_texture_catalog_aov(row['files']['effect'],row['files'].get('effect_raw'))
        except Exception:
            raw_catalog=[]
        if raw_catalog:
            catalog=[{'name':x['name'],'hues':[],'format':x.get('format','')} for x in raw_catalog]
            ui.info('Không đọc được pixel của texture nén; vẫn tải danh sách Texture2D để chọn. Texture không decode được sẽ dùng Material tint.')
        elif not catalog:
            ui.info('Không quét được Texture2D; màu sẽ áp qua Material của FX nếu có.')
            return {'texture_names':None}
    ans=ask_yes_no('Có muốn chỉnh riêng Texture2D không? Y/N')
    if ans is None: return None
    if ans=='n': return {'texture_names':None}
    print(); print(ui.B+' DANH SÁCH TEXTURE2D CỦA FX'+ui.R); ui.rule()
    for i,it in enumerate(catalog,1):
        hs=', '.join(_fmt_hue(h) for h in it.get('hues',[])[:3]) if it.get('hues') else 'không đọc được màu'
        extra=(' ['+str(it.get('format'))+']') if it.get('format') else ''
        print(' %s%2d.%s %s%s  %s%s%s'%(ui.CY,i,ui.R,it['name'],extra,ui.DIM,hs,ui.R))
    ui.rule()
    while True:
        raw=input(ui.B+' Chọn Texture2D theo số (nhiều cái cách nhau bằng dấu phẩy): '+ui.R).strip(); picked=_parse_multi_int(raw,len(catalog))
        if picked: return {'texture_keys':[catalog[i-1]['key'] for i in picked], 'texture_names':[catalog[i-1]['name'] for i in picked]}
        ui.err('Sai cú pháp. Vui lòng chọn lại')

def ask_source_hues(row,texture_keys):
    try: catalog=fx_engine.scan_fx_texture_catalog_aov(row['files']['effect'],row['files'].get('effect_raw'))
    except Exception: return None
    keys=set(texture_keys or [x['key'] for x in catalog]); bins={}
    for it in catalog:
        if it['key'] not in keys: continue
        for h in it.get('hues',[]): bins[round(float(h),2)]=bins.get(round(float(h),2),0)+1
    hues=sorted(bins)
    if not hues: return None
    ui.info('BẢNG MÀU ĐÃ QUÉT TỪ TEXTURE2D')
    for st in range(0,len(hues),3):
        print('    '.join('%s%2d.%s Hue %s'%(ui.CY,j+1,ui.R,_fmt_hue(hues[j])) for j in range(st,min(st+3,len(hues)))))
    while True:
        raw=input(ui.B+' Có muốn chỉnh riêng màu nguồn không? Y/N: '+ui.R).strip().lower()
        if raw=='n': return None
        if raw=='y':
            while True:
                pick=input(ui.B+' Chọn màu nguồn theo số (nhiều cái bằng dấu phẩy): '+ui.R).strip(); vals=_parse_multi_int(pick,len(hues))
                if vals: return [hues[i-1] for i in vals]
                ui.err('Sai cú pháp. Vui lòng chọn lại')
        else: ui.err('Sai cú pháp. Vui lòng chọn lại')

def ask_gray_targets():
    print(); print(ui.B+' MÀU CƠ BẢN CẦN CHỈNH'+ui.R)
    print('  1. Trắng'); print('  2. Đen'); print('  3. Xám'); print('  4. Cả ba'); print('  0. Giữ nguyên')
    while True:
        raw=input(ui.B+' Chọn: '+ui.R).strip()
        if raw=='0': return []
        if raw=='4': return ['white','black','gray']
        vals=_parse_multi_int(raw,3)
        if vals: return [('white','black','gray')[i-1] for i in vals]
        ui.err('Sai cú pháp. Vui lòng chọn lại')

def ask_color_spec(row, confirm=True):
    # MÀU LÀ LUỒNG RIÊNG: tuyệt đối không gọi show_fx_menu()/configure_effects().
    # row luôn chứa files để quét đúng effect của ID hiện tại.
    if confirm:
        yn=ask_yes_no('Có muốn điều chỉnh màu của ID %s - %s? Y/N'%(ui.CY+ui.B+str(row.get('id',''))+ui.R,ui.YL+_plain_color_label(row)+ui.R))
        if yn is None: return None
        if yn=='n': return {'keep':True}
    while True:
        print(); print('  1. Đổi màu'); print('  2. Pha màu'); print('  0. Bỏ qua ID này')
        mode=input(ui.B+' Chọn: '+ui.R).strip()
        if mode in ('0','1','2'): break
        ui.err('Sai cú pháp. Vui lòng chọn lại')
    if mode=='0': return {'keep':True}
    scope=ask_texture_scope(row)
    if scope is None: return None
    src_hues=ask_source_hues(row,scope.get('texture_keys'))
    gray=ask_gray_targets()
    if mode=='1':
        return {'mode':'replace','target_rgb':ask_palette_rgb(),'keep':False,'texture_names':scope.get('texture_names'),'texture_keys':scope.get('texture_keys'),'selected_hues':src_hues,'gray_targets':gray}
    while True:
        raw=input(ui.B+' Số màu muốn pha (2-4): '+ui.R).strip()
        if raw.isdigit() and 2<=int(raw)<=4: count=int(raw); break
        ui.err('Sai cú pháp. Vui lòng chọn lại!')
    mix=[]
    for k in range(count):
        print(ui.B+' Màu pha số %d/%d'%(k+1,count)+ui.R); rgb=ask_palette_rgb()
        while True:
            raw=input(ui.B+' Tỷ lệ (%): '+ui.R).strip()
            if not re.fullmatch(r'(?:\d+(?:\.\d+)?|\.\d+)',raw): ui.err('Sai cú pháp. Vui lòng chọn lại!'); continue
            pct=float(raw)
            if pct<=0 or pct>100: ui.err('Sai cú pháp. Vui lòng chọn lại!'); continue
            mix.append((rgb,pct)); break
    if abs(sum(p for _,p in mix)-100)>0.01:
        ui.err('Tổng tỷ lệ phải bằng 100%. Vui lòng chọn lại phần pha màu.'); return ask_color_spec(row, confirm=False)
    return {'mode':'mix','mix_rgb':fx_engine._mix_rgb(mix),'keep':False,'texture_names':scope.get('texture_names'),'texture_keys':scope.get('texture_keys'),'selected_hues':src_hues,'gray_targets':gray}


def configure_colors_selected(effect_layers):
    if not effect_layers:
        return effect_layers
    out=[]
    for spec in effect_layers:
        if spec.get('default') or not spec.get('effect'):
            out.append(dict(spec)); continue
        if ask_yes_no('Có muốn điều chỉnh màu cho %s? Y/N' % _row_label(spec)) != 'y':
            out.append(dict(spec)); continue
        row={'id':spec.get('id',''),'name':spec.get('name',''),'hero':spec.get('hero',''),
             'files':{'effect':spec.get('effect'),'effect_raw':spec.get('effect_raw')}}
        c=ask_color_spec(row, confirm=False)
        if c is None: return None
        ns=dict(spec); ns['color']=c; out.append(ns)
    return out


def configure_textures_selected(effect_layers):
    """Cho chọn Texture2D của từng FX để tắt phần hình ảnh sử dụng texture đó."""
    out=[]
    for spec in effect_layers:
        if spec.get('default') or not spec.get('effect'):
            out.append(dict(spec)); continue
        row={'id':spec.get('id',''),'name':spec.get('name',''),'hero':spec.get('hero',''),
             'files':{'effect':spec.get('effect'),'effect_raw':spec.get('effect_raw')}}
        try:
            textures=fx_engine.list_fx_texture_catalog(row['files']['effect'], row['files'].get('effect_raw'))
        except Exception as ex:
            ui.err('Không đọc được Texture2D của ID %s: %s' % (row['id'], ex))
            out.append(dict(spec)); continue
        print(); print(ui.B+' CÁC TEXTURE2D CỦA '+_plain_color_label(row)+ui.R); ui.rule()
        if not textures:
            ui.warn('Không tìm thấy Texture2D trong FX này.'); out.append(dict(spec)); continue
        for i,it in enumerate(textures,1):
            fmt=('  ['+str(it.get('format'))+']') if it.get('format') else ''
            print(' %s%2d.%s %s%s' % (ui.CY,i,ui.R,it.get('name') or ('Texture2D %s'%i),fmt))
        ui.rule(); print(ui.DIM+'  0 = giữ nguyên toàn bộ Texture2D'+ui.R)
        while True:
            raw=input(ui.B+' Chọn Texture2D muốn XÓA khỏi phần hiệu ứng (nhiều cái bằng dấu phẩy): '+ui.R).strip()
            if raw=='0': selected=[]; break
            vals=_parse_multi_int(raw,len(textures))
            if vals:
                selected=[int(textures[i-1]['path_id']) for i in vals]
                break
            ui.err('Sai cú pháp. Vui lòng chọn lại')
        ns=dict(spec); ns['disabled_textures']=selected; out.append(ns)
        if selected:
            ui.info('  → Đã chọn %d Texture2D. Phần hiệu ứng dùng các texture này sẽ bị tắt.'%len(selected))
    return out


def _ask_percentage(prompt):
    while True:
        raw=input(ui.B+prompt+ui.R+' ').strip()
        if not re.fullmatch(r'(?:\d+(?:\.\d+)?|\.\d+)',raw):
            ui.err('Sai cú pháp. Vui lòng chọn lại!'); continue
        try: v=float(raw)
        except Exception: ui.err('Sai cú pháp. Vui lòng chọn lại!'); continue
        if not 0<=v<=100:
            ui.err('Vui lòng nhập từ 0 đến 100.'); continue
        return v


def configure_opacity_selected(effect_layers):
    out=[]
    for spec in effect_layers:
        if spec.get('default') or not spec.get('effect'):
            out.append(dict(spec)); continue
        if ask_yes_no('Có muốn điều chỉnh độ trong suốt cho %s? Y/N' % _row_label(spec)) != 'y':
            out.append(dict(spec)); continue
        label=_row_label(spec)
        print(); print(ui.B+' Độ trong suốt của '+label+ui.R)
        print(ui.DIM+'  100% = rõ hoàn toàn · 0% = trong suốt hoàn toàn'+ui.R)
        val=_ask_percentage('Nhập độ trong suốt (%):')
        ns=dict(spec); ns['opacity']=val/100.0; out.append(ns)
    return out


def configure_scale_xy_selected(effect_layers):
    out=[]
    for spec in effect_layers:
        if spec.get('default') or not spec.get('effect'):
            out.append(dict(spec)); continue
        row={'id':spec.get('id',''),'name':spec.get('name',''),'hero':spec.get('hero',''),
             'files':{'effect':spec.get('effect'),'effect_raw':spec.get('effect_raw')}}
        try:
            tr=fx_engine.get_fx_transform(row['files']['effect'], row['files'].get('effect_raw'))
            cur=tr.get('scale') or {'x':1.0,'y':1.0}
        except Exception:
            cur={'x':1.0,'y':1.0}
        if spec.get('size') is not None:
            cur={'x':float(spec['size']),'y':float(spec['size'])}
        if ask_yes_no('Có muốn chỉnh kích thước Ngang / Thẳng cho %s? Y/N' % _row_label(row)) != 'y':
            out.append(dict(spec)); continue
        print(); print(ui.B+' Kích thước hiện tại của '+_row_label(row)+ui.R)
        print('  Ngang : %.6g' % float(cur.get('x',1.0)))
        print('  Thẳng : %.6g' % float(cur.get('y',1.0)))
        print(ui.DIM+'  Đây là kích thước, không phải vị trí.'+ui.R)
        x=_ask_number('Kích thước Ngang muốn đặt:', allow_negative=False)
        yv=_ask_number('Kích thước Thẳng muốn đặt:', allow_negative=False)
        ns=dict(spec); ns['scale_xy_override']={'x':x,'y':yv}; out.append(ns)
    return out



def configure_size_selected(effect_layers):
    out=[]
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'):
            out.append(dict(sp)); continue
        if ask_yes_no('Có muốn điều chỉnh Size cho %s? Y/N' % _row_label(sp)) != 'y':
            out.append(dict(sp)); continue
        row={'id':sp['id'],'name':sp['name'],'hero':sp.get('hero',''),
             'files':{'effect':sp['effect'],'effect_raw':sp.get('effect_raw')}}
        size=ask_positive_size(row)
        if size is None: return None
        ns=dict(sp); ns['size']=size; out.append(ns)
    return out


def configure_align_selected(effect_layers, initial_picked):
    """Căn riêng từng FX theo effect gốc của skin/button đã chọn ở đầu."""
    if not initial_picked:
        return effect_layers
    anchor = initial_picked[0]
    anchor_row={'id':anchor.get('id',''),'name':anchor.get('name',''),'hero':anchor.get('hero',''),
                'files':{'effect':anchor['files'].get('effect'),'effect_raw':anchor['files'].get('effect_raw')}}
    out=[]
    for sp in effect_layers:
        ns=dict(sp)
        if sp.get('default') or not sp.get('effect') or str(sp.get('id'))==str(anchor.get('id')):
            out.append(ns); continue
        if ask_yes_no('Có muốn fix lệch cho %s theo ID %s? Y/N' % (_row_label(sp), ui.CY+ui.B+str(anchor.get('id'))+ui.R)) != 'y':
            out.append(ns); continue
        row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
             'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
        try:
            pos,_=_effective_position(row,anchor_row,True)
        except Exception:
            pos={'x':0.0,'y':0.0,'z':0.0}
        ns['position_override']={'x':float(pos.get('x',0.0)),'y':float(pos.get('y',0.0)),'z':float(pos.get('z',0.0))}
        ui.info('  → %s đã lấy vị trí theo %s' % (_row_label(sp), ui.CY+ui.B+str(anchor.get('id'))+ui.R))
        out.append(ns)
    return out


def _editable_indices(effect_layers):
    return [i for i,s in enumerate(effect_layers,1) if not s.get('default') and s.get('effect')]


def _print_spec_list(effect_layers, title='Danh sách hiệu ứng'):
    print(); print(ui.B+title+ui.R); ui.rule()
    for i,sp in enumerate(effect_layers,1):
        tag='MẶC ĐỊNH' if sp.get('default') else _row_label(sp)
        print(' %s%2d.%s %s' % (ui.CY, i, ui.R, tag))
    ui.rule()


def _parse_spec_indices(raw, effect_layers, min_count=1):
    vals=_parse_multi_int(raw,len(effect_layers))
    vals=[v for v in vals if v in _editable_indices(effect_layers)]
    return vals if len(vals)>=min_count else []


def configure_layer_order(effect_layers):
    editable=_editable_indices(effect_layers)
    if len(editable)<2:
        ui.warn('Cần ít nhất 2 hiệu ứng để chỉnh thứ tự hiển thị.')
        return effect_layers
    _print_spec_list(effect_layers,'THỨ TỰ HIỂN THỊ HIỆN TẠI')
    print(ui.DIM+'  Nhập thứ tự từ DƯỚI lên TRÊN. Ví dụ: 2,1,3 → FX số 2 nằm dưới cùng.'+ui.R)
    while True:
        raw=input(ui.B+' Thứ tự mới: '+ui.R).strip()
        vals=_parse_multi_int(raw,len(effect_layers))
        if vals and len(vals)==len(editable) and set(vals)==set(editable):
            break
        ui.err('Phải nhập đủ tất cả FX, mỗi số đúng một lần. Ví dụ: 2,1,3')
    for layer, idx in enumerate(vals,1):
        effect_layers[idx-1]['layer']=layer
    ui.info('Đã đổi thứ tự hiển thị: '+', '.join(str(v) for v in vals))
    return effect_layers


def configure_copy_settings(effect_layers):
    editable=_editable_indices(effect_layers)
    if len(editable)<2:
        ui.warn('Cần ít nhất 2 hiệu ứng để sao chép cài đặt.')
        return effect_layers
    _print_spec_list(effect_layers,'SAO CHÉP CÀI ĐẶT')
    while True:
        raw=input(ui.B+' Chọn FX nguồn (1 số): '+ui.R).strip()
        vals=_parse_spec_indices(raw,effect_layers,1)
        if len(vals)==1: src_idx=vals[0]-1; break
        ui.err('Vui lòng chọn đúng 1 FX nguồn.')
    while True:
        raw=input(ui.B+' Chọn FX đích (nhiều cái bằng dấu phẩy): '+ui.R).strip()
        vals=_parse_spec_indices(raw,effect_layers,1)
        vals=[v for v in vals if v-1 != src_idx]
        if vals: break
        ui.err('Vui lòng chọn ít nhất 1 FX đích khác FX nguồn.')
    _boxed_menu('CHỌN PHẦN MUỐN SAO CHÉP', [
        '1. Tất cả cài đặt chỉnh riêng',
        '2. Vị trí',
        '3. Xoay',
        '4. Size',
        '5. Độ trong suốt',
        '6. Kích thước Ngang / Thẳng',
        '7. Độ sáng',
        '8. Màu',
        '9. Đảo chiều xoay',
    ])
    while True:
        raw=input(ui.B+' Chọn phần (có thể nhập nhiều số): '+ui.R).strip()
        parts=_parse_multi_int(raw,9)
        if parts: break
        ui.err('Sai cú pháp. Vui lòng chọn lại')
    if 1 in parts: keys=['position_override','rotation_z_override','size','opacity','scale_xy_override','brightness','color','reverse_rotation']
    else:
        keys=[]
        mp={2:'position_override',3:'rotation_z_override',4:'size',5:'opacity',6:'scale_xy_override',7:'brightness',8:'color',9:'reverse_rotation'}
        for k,v in mp.items():
            if k in parts: keys.append(v)
    src=effect_layers[src_idx]
    for v in vals:
        dst=effect_layers[v-1]
        for k in keys:
            if k in src:
                dst[k]=copy.deepcopy(src[k]) if k in src else dst.get(k)
            else:
                dst.pop(k,None)
    ui.info('Đã sao chép từ '+_row_label(src)+' sang '+', '.join(_row_label(effect_layers[v-1]) for v in vals))
    return effect_layers


def configure_restore_settings(effect_layers):
    editable=_editable_indices(effect_layers)
    if not editable:
        ui.warn('Không có FX để khôi phục.')
        return effect_layers
    _print_spec_list(effect_layers,'KHÔI PHỤC CÀI ĐẶT GỐC')
    while True:
        raw=input(ui.B+' Chọn FX muốn khôi phục (nhiều cái bằng dấu phẩy): '+ui.R).strip()
        vals=_parse_spec_indices(raw,effect_layers,1)
        if vals: break
        ui.err('Sai cú pháp. Vui lòng chọn lại')
    _boxed_menu('CHỌN PHẦN MUỐN KHÔI PHỤC', [
        '1. Tất cả cài đặt chỉnh riêng',
        '2. Vị trí',
        '3. Xoay',
        '4. Size',
        '5. Độ trong suốt',
        '6. Kích thước Ngang / Thẳng',
        '7. Độ sáng',
        '8. Màu',
        '9. Đảo chiều xoay',
    ])
    while True:
        raw=input(ui.B+' Chọn phần (có thể nhập nhiều số): '+ui.R).strip()
        parts=_parse_multi_int(raw,9)
        if parts: break
        ui.err('Sai cú pháp. Vui lòng chọn lại')
    if 1 in parts: keys=['position_override','rotation_z_override','size','opacity','scale_xy_override','brightness','color','reverse_rotation']
    else:
        mp={2:'position_override',3:'rotation_z_override',4:'size',5:'opacity',6:'scale_xy_override',7:'brightness',8:'color',9:'reverse_rotation'}
        keys=[v for k,v in mp.items() if k in parts]
    for v in vals:
        sp=effect_layers[v-1]
        for k in keys:
            sp.pop(k,None)
        if 'size' in keys: sp['size']=None
    ui.info('Đã khôi phục cài đặt gốc cho '+', '.join(_row_label(effect_layers[v-1]) for v in vals))
    return effect_layers

def configure_position_selected(effect_layers, initial_picked, align_to_button):
    rows_by_id={str(r['id']):r for r in initial_picked}
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'): continue
        if ask_yes_no('Có muốn chỉnh vị trí cho %s? Y/N' % _row_label(sp)) != 'y': continue
        row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
             'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
        anchor_row=rows_by_id.get(str(initial_picked[0].get('id'))) if initial_picked else None
        try: pos,_=_effective_position(row,anchor_row,align_to_button)
        except Exception: pos={'x':0.0,'y':0.0,'z':0.0}
        print(); print(ui.B+' Vị trí hiện tại của '+_row_label(row)+ui.R)
        print('  Ngang : %.6g'%float(pos.get('x',0.0)))
        print('  Thẳng : %.6g'%float(pos.get('y',0.0)))
        print(ui.DIM+'  (+ Ngang = sang phải, - Ngang = sang trái)'+ui.R)
        print(ui.DIM+'  (+ Thẳng = lên trên, - Thẳng = xuống dưới)'+ui.R)
        dx=_ask_number_or_skip('Muốn dịch Ngang bao nhiêu? (+ phải / - trái)')
        dy=_ask_number_or_skip('Muốn dịch Thẳng bao nhiêu? (+ lên / - xuống)')
        dz=_ask_number_or_skip('Muốn dịch Pos Z bao nhiêu? (+ trước / - sau)')
        x=float(pos.get('x',0.0)) if dx is None else float(pos.get('x',0.0))+dx
        y=float(pos.get('y',0.0)) if dy is None else float(pos.get('y',0.0))+dy
        z=float(pos.get('z',0.0)) if dz is None else float(pos.get('z',0.0))+dz
        sp['position_override']={'x':x,'y':y,'z':z}
    return effect_layers


def configure_rotation_selected(effect_layers):
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'): continue
        if ask_yes_no('Có muốn xoay hiệu ứng cho %s? Y/N' % _row_label(sp)) != 'y': continue
        row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
             'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
        try: _,rz=_effective_position(row,None,False)
        except Exception: rz=0.0
        print(); print(ui.B+' Góc xoay hiện tại của '+_row_label(row)+': %.6g°'%rz+ui.R)
        print(ui.DIM+'  Nhập 62 = 62° · số âm = xoay ngược chiều'+ui.R)
        sp['rotation_z_override']=_ask_number('Muốn xoay thành bao nhiêu độ?')
    return effect_layers



def configure_brightness_selected(effect_layers):
    out=[]
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'):
            out.append(dict(sp)); continue
        if ask_yes_no('Có muốn điều chỉnh độ sáng cho %s? Y/N' % _row_label(sp)) != 'y':
            out.append(dict(sp)); continue
        print(ui.DIM+'  100% = giữ nguyên · 0% = tối hoàn toàn · 200% = sáng gấp đôi'+ui.R)
        while True:
            val=_ask_number('Độ sáng (%):', allow_negative=False)
            if 0 <= val <= 300: break
            ui.err('Vui lòng nhập từ 0 đến 300.')
        ns=dict(sp); ns['brightness']=val/100.0; out.append(ns)
    return out


def configure_part_scale_selected(effect_layers):
    out=[]
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'):
            out.append(dict(sp)); continue
        if ask_yes_no('Có muốn điều chỉnh độ phóng đại từng phần cho %s? Y/N' % _row_label(sp)) != 'y':
            out.append(dict(sp)); continue
        row={'id':sp.get('id',''),'name':sp.get('name',''),'hero':sp.get('hero',''),
             'files':{'effect':sp.get('effect'),'effect_raw':sp.get('effect_raw')}}
        try: parts=fx_engine.get_fx_parts(row['files']['effect'], row['files'].get('effect_raw'))
        except Exception as ex:
            ui.err('Không đọc được cấu trúc FX: %s'%ex); out.append(dict(sp)); continue
        if not parts:
            ui.warn('FX này không có phần hình ảnh để chỉnh.'); out.append(dict(sp)); continue
        print(); print(ui.B+' CÁC PHẦN CÓ THỂ PHÓNG TO/THU NHỎ CỦA '+_row_label(row)+ui.R); ui.rule()
        for i,it in enumerate(parts,1):
            indent='  '*min(int(it.get('depth',0)),3)
            comps=', '.join(it.get('components') or [])
            print('%s%s%2d.%s %s%s' % (indent,ui.CY,i,ui.R,it.get('name','?'),(' ['+comps+']' if comps else '')))
        ui.rule()
        while True:
            raw=input(ui.B+' Chọn phần (nhiều cái bằng dấu phẩy, 0 = bỏ qua): '+ui.R).strip()
            if raw=='0': vals=[]; break
            vals=_parse_multi_int(raw,len(parts))
            if vals: break
            ui.err('Sai cú pháp. Vui lòng chọn lại')
        overrides=[]
        for idx in vals:
            part=parts[idx-1]
            print(); ui.info('Phần %d - %s'%(idx,part.get('name','?')))
            factor=_ask_number('Độ phóng đại (1 = giữ nguyên, 2 = gấp đôi, 0.5 = một nửa):', allow_negative=False)
            overrides.append({'transform_path_id':int(part['transform_path_id']),'factor':float(factor)})
        ns=dict(sp); ns['part_scale_overrides']=overrides; out.append(ns)
    return out

def configure_reverse_rotation_selected(effect_layers):
    """Đảo chiều chuyển động nhìn thấy của FX 2D bằng cách lật ngang root FX.

    Không đụng ParticleSystem timing/rotation fields; giữ nguyên tốc độ và các state
    runtime đã ổn định. Với một FX 2D quay quanh Z, phản chiếu một trục sẽ đảo
    handedness của chuyển động nhìn thấy: ↻ <-> ↺.
    """
    for sp in effect_layers:
        if sp.get('default') or not sp.get('effect'):
            continue
        if ask_yes_no('Có muốn đảo chiều xoay cho %s? Y/N' % _row_label(sp)) != 'y':
            continue
        sp['reverse_rotation'] = not bool(sp.get('reverse_rotation'))
        ui.info('  → Đảo chiều xoay: %s' % ('BẬT' if sp['reverse_rotation'] else 'TẮT'))
    return effect_layers

def run_session(rows, btn_bundle):
    ui.clear()
    ui.banner()
    show_menu(rows)
    print()
    try:
        raw = input(ui.B + ' Vui long nhap ID Button muon mod ' + ui.R
                    + ui.DIM + '(so thu tu hoac ID, nhieu cai cach nhau bang dau cach, q = thoat): ' + ui.R).strip()
    except (EOFError, KeyboardInterrupt):
        return False
    if raw.lower() in ('q', 'quit', 'exit'):
        return False

    picked, bad = parse_ids(raw, rows)
    if bad or not picked:
        ui.err('Sai cú pháp. Vui lòng chọn lại')
        return True

    print()
    ui.rule('=')
    for r in picked:
        print(' %s%-7s%s %s%s%s %s%s%s'
              % (ui.CY + ui.B, r['id'], ui.R, ui.B, r['name'], ui.R,
                 ui.DIM, ('· ' + r['hero']) if r['hero'] else '', ui.R))
    ui.rule('=')
    print()

    effect_config = configure_effects(rows, picked)
    if effect_config is False:
        return True
    effect_layers = effect_config.get('specs') if effect_config else None
    align_to_button = bool(effect_config.get('align_to_button')) if effect_config else False
    if effect_layers:
        print()
        ui.info('FX rieng da chon: ' + ', '.join('%s (%s)' % (x['id'], (('%s %s' % ((x.get('hero') or '').strip(), x['name'])).strip() if x.get('hero') else x['name'])) for x in effect_layers))
        if align_to_button:
            ui.info('FIX lệch: dùng pos của ID %s làm mốc' % picked[0]['id'])
        print()
        global _CURRENT_ROWS_BY_ID
        _CURRENT_ROWS_BY_ID = {str(r['id']): r for r in rows}

        if effect_config.get('use_clone'):
            effect_layers = configure_clone_selected(effect_layers)
        if effect_config.get('use_align'):
            effect_layers = configure_align_selected(effect_layers, picked)
            align_to_button = False
        if effect_config.get('use_order'):
            effect_layers = configure_layer_order(effect_layers)
        if effect_config.get('use_size'):
            effect_layers = configure_size_selected(effect_layers)
            if effect_layers is None:
                return True
        if effect_config.get('use_position'):
            effect_layers = configure_position_selected(effect_layers, picked, False)
        if effect_config.get('use_rotation'):
            effect_layers = configure_rotation_selected(effect_layers)
        if effect_config.get('use_opacity'):
            effect_layers = configure_opacity_selected(effect_layers)
        if effect_config.get('use_scale_xy'):
            effect_layers = configure_scale_xy_selected(effect_layers)
        if effect_config.get('use_brightness'):
            effect_layers = configure_brightness_selected(effect_layers)
        if effect_config.get('use_color'):
            effect_layers = configure_colors_selected(effect_layers)
        if effect_config.get('use_copy'):
            effect_layers = configure_copy_settings(effect_layers)
        if effect_config.get('use_restore'):
            effect_layers = configure_restore_settings(effect_layers)
        if effect_config.get('use_reverse_rotation'):
            effect_layers = configure_reverse_rotation_selected(effect_layers)
        if effect_config.get('use_preset'):
            _preset_result = preset_menu(effect_layers, picked, align_to_button)
            if _preset_result is None:
                return True
            effect_layers, align_to_button = _preset_result
        print()

    # Không có điều chỉnh FX riêng: không cần hỏi lại màu.
    color_by_sid = {}

    done, fail = [], []
    for r in picked:
        sid = r['id']
        label = '%s  %s' % (sid, r['name'][:24])
        state = {'n': 0}

        def step():
            state['n'] += 1
            ui.bar(state['n'], STEPS, label)

        logs = []
        ui.bar(0, STEPS, label)
        out = os.path.join(OUT_DIR, sid, OUT_REL, 'battleotherui.assetbundle')
        t0 = time.time()
        try:
            _local_effect_layers = effect_layers if effect_layers is not None else color_by_sid.get(sid)
            size = graft.build_one(sid, r['files'], btn_bundle, out,
                                   log=logs.append, step=step,
                                   button_dir=BTN_DIR,
                                   out_dir=os.path.dirname(out),
                                   effect_layers=_local_effect_layers,
                                   align_to_button=align_to_button)
            # keo theo battleotherui_raw neu co
            raw_src = os.path.join(BTN_DIR, 'battleotherui_raw.assetbundle')
            if os.path.isfile(raw_src):
                shutil.copy2(raw_src, os.path.join(os.path.dirname(out),
                                                   'battleotherui_raw.assetbundle'))
            for l in logs:
                ui.info(l)
            ui.ok('  Done [%s] \u2713  %.2f MB  ·  %.1fs'
                  % (sid, size / 1048576.0, time.time() - t0))
            print(ui.DIM + '   -> Output/%s/%s/' % (sid, OUT_REL.replace(os.sep, '/')) + ui.R)
            done.append(sid)
        except Exception as e:
            print()
            ui.err('  [X] Loi [%s]: %s' % (sid, e))
            if os.environ.get('AOV_DEBUG'):
                traceback.print_exc()
            fail.append(sid)
        print()

    ui.rule('=')
    if done:
        ui.ok(' Hoan tat: ' + '  '.join('[%s]\u2713' % d for d in done))
    if fail:
        ui.err(' That bai: ' + '  '.join('[%s]\u2717' % d for d in fail))
    ui.rule('=')
    try:
        input(ui.B + '\n Enter de chay phien moi...' + ui.R)
    except (EOFError, KeyboardInterrupt):
        return False
    return True


def main():
    btn, skn = preflight()
    ui.clear()
    ui.banner()
    ui.info('\n  Dang quet Source va doi chieu skin.txt...')
    rows = build_menu(SRC_DIR, skn)
    if not rows:
        ui.err('  [X] Source/ khong co file personalbutton* nao.')
        sys.exit(1)
    while run_session(rows, btn):
        pass
    print()
    ui.info(' Tam biet.')


if __name__ == '__main__':
    main()
