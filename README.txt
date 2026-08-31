================================================================
  AOV  BUTTON & BANNER MODDER   -  huong dan
================================================================

CAU TRUC THU MUC
----------------
  run.py                  <- chay cai nay
  core/                   loi tool (khong sua)
  lib/                    UnityPy (fork AOV) + Protect.py
  Source/                 personalbuttoneffect_<ID>.assetbundle
                          personalbuttoneffect_<ID>_raw.assetbundle
                          personalbuttonsprite_<ID>_raw.assetbundle
  Button/                 battleotherui.assetbundle       (CHUA MOD - bat buoc)
                          battleotherui_raw.assetbundle   (tuy chon)
                          battlecommon.assetbundle        (tuy chon - icon shop)
                          battlecommon_raw.assetbundle    (tuy chon - icon shop)
  Skin/skin.txt           danh sach ID - ten skin
  Output/                 ket qua

CHAY
----
  python run.py

  Tren Termux:  pkg install python
                pip install lz4 brotli pycryptodome sm4 pillow
                python run.py

  Tren Pydroid 3: mo run.py roi bam Run.

CACH DUNG
---------
  1. Tool clear man hinh, quet Source va doi chieu skin.txt
  2. Hien danh sach:   1.[Ten Skin] [ID] [FX+JOY]
  3. Nhap ID muon mod. Nhieu ID thi cach nhau bang dau cach:
        59901 13215 10618
     Cung nhap duoc so thu tu trong danh sach.
  4. Thanh tien trinh chay cho tung ID
  5. Xong -> Done [ID] v
  6. Enter de chay phien moi. Go q de thoat.

KET QUA
-------
  Output/<ID>/Resources/1.63.1/assetbundle/uisystem/battle/
        battleotherui.assetbundle       <- FX + joystick, da ma hoa
        battleotherui_raw.assetbundle   <- copy nguyen ban
        battlecommon.assetbundle        <- icon shop (neu co file goc)
        battlecommon_raw.assetbundle    <- icon shop (neu co file goc)

  Chep nguyen thu muc Resources/ vao game.

NHAN
----
  FX   = co personalbuttoneffect  -> mod duoc hieu ung nut danh
  JOY  = co personalbuttonsprite_raw -> mod duoc joystick + vien chieu

KIEN TRUC (gop tu 2 tool da chay tot — KHONG viet lai logic)
------------------------------------------------------------
  core/fx_engine.py    loi FX lay NGUYEN VEN tu QuanBeo
                       - gop bang external cua file effect vao battleotherui
                         roi remap fileID (khong quet mu byte)
                       - INLINE Texture2D cua FX -> khong con phu thuoc .resS
                       - tu them SerializedType con thieu (SortingGroup / AnimationClip)

  core/joy_engine.py   loi JOYSTICK lay NGUYEN VEN tu AovButton
                       - 2 bo joystick (Joystick + Joystick_Camera)
                       - vien chieu, nut danh, nut tru, danh linh, khoa tuong/linh
                       - BorderIndicatorUp / BorderIndicatorDown (164x144 native)
                       - S2 atlas/standalone, S3 inline atlas, G1 mirror, G2 border

  core/shop_engine.py  nhanh SHOP — icon cua hang trong battlecommon*
                       - BattleShop_Entrance        <- CustomJoyStick_ShopIcon
                       - BattleShop_Entrance_OnRight <- BattleShop_Entrance_OnRight
                       - GHI DE TAI CHO (giu PathID + m_Name) vi slot OnRight
                         khong co Image nao tro tinh, game doi luc runtime
                       - Thieu file battlecommon* thi tu bo qua, khong loi

  core/graft.py        chi noi cac loi lai:
                       decrypt -> FX -> JOY -> save(lzma) -> encrypt -> SHOP

TOOL LAM GI (theo AOV_battleotherui_graft_rules.md)
---------------------------------------------------
  R1  do root 'attackbutton' khong phan biet hoa thuong
  R2  root la neo rong -> mount o (0,0,0) scale 1, khong cong offset 2 lan
  R3  neu node mount la RectTransform -> ghi luon m_AnchoredPosition
  S1  tro m_Sprite cua Image (5 slot joystick tro dich danh, 18 slot theo sprite goc)
  S2  tu nhan biet sprite atlas-backed / standalone
  S3  inline texture, KHONG dung toi .resS
  G1  mirror joystick bat/tat theo be rong RockingBg (145 = manh 1/4, 290 = full)
  G2  bu BorderIndicator khi RockingArrow la 164x144

  Tu them SerializedType (SortingGroup / AnimationClip ...) neu battleotherui thieu.

LOI THUONG GAP
--------------
  [X] Khong thay UnityPy / Protect.py
      -> chep 'UnityPy/' va 'Protect.py' vao lib/

  Muon xem traceback day du:  AOV_DEBUG=1 python run.py
