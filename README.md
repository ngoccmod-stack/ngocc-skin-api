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
