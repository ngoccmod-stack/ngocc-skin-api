NGOCC BACKEND - READY TO COPY INTO EXISTING REPO

Copy the contents of this folder into the ROOT of the existing repository:
ngoccmod-stack/ngocc-skin-api

Do NOT upload this folder itself as a nested directory.
Do NOT upload this zip into the repository.
Do NOT delete Resources/<version> unless intentionally replacing it.

This package fixes:
- missing find_resource_versions import in server.py
- keeps Resources version-discovery dynamic
- keeps chunked Resources upload endpoints

server_patch.py was intentionally excluded because it is an old local patch helper
that references /mnt/data/v3inspect/ngocc_v3 and is not needed by the production server.
