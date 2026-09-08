# NGOCC Skin System V2

Backend cho NGOCC MOD:
- Quản lý Resources theo version, không hard-code 1.55.1.
- Scan `heroSkin.bytes` + VN language maps để tạo catalog ID/tướng/skin.
- Chỉ khi Admin chủ bấm scan mới truy cập Garena để lấy ảnh tướng/skin.
- Web đọc catalog đã lưu, không scan Garena mỗi lần khách vào.
- Build ZIP Mod Skin bằng AutoMod ở backend, cache theo `skinId + Resources version`.

## Chạy
1. Đặt `Resources/<version>/...` bên cạnh server.py hoặc upload qua `/api/resources/upload`.
2. `pip install -r requirements.txt`
3. `python -m uvicorn server:app --host 0.0.0.0 --port 8000`

## API
GET `/api/health`
GET `/api/catalog`
POST `/api/scan`
POST `/api/resources/upload` multipart field `file`
POST `/api/check` JSON `{ "ids": ["14117"] }`
POST `/api/build/{skin_id}`
GET `/download/{file}`

## Web
Đặt URL backend vào ô `Skin API URL` của Admin chủ. Nếu web và backend cùng origin thì có thể để URL tương đối theo cấu hình trang.

## Lưu ý
AutoMod gốc là CLI và có các nhánh xử lý đặc biệt. V2 chạy một lần không tương tác với các lựa chọn an toàn mặc định:
- Other function: N
- iOS: N
- Anti-dec: N
- Cam xa: N
- 52007 component: No Mod Component
- 54402 special: N
- Nakroth killboard: Không

Builder dùng một workspace riêng để không sửa Resources master.


## Button ZIP upload (V13)
The web upload button expects one outer ZIP containing many per-skin ZIP files. The browser reads the outer ZIP locally, matches each inner ZIP name to the saved button catalog, and uploads each inner ZIP directly to Cloudinary as an individual `raw` asset. This avoids the Cloudinary Free 10 MB raw-file limit on the outer archive and avoids long uploads through Render. The catalog stores the original inner ZIP filename so downloads keep the exact filename supplied by the uploader.

## v10 skin catalog fixes
- Uses the supplied `#1Nút Bấm/Skin/skin.txt` to resolve real 5-digit skin IDs when Garena exposes only skin names/slots.
- Skin cards use a large 16:9 rectangular artwork area.
- Added `/api/catalog/issues` plus admin endpoints for mismatched IDs, unresolved IDs, and missing images.
- Manual skin ID assignment is persisted across rescans and marks the skin ready for Auto Mod when that ID exists in the current Resources index.
- Mismatched IDs can be ignored/deleted from the public catalog so they do not return on later scans.
