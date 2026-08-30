from pathlib import Path
p=Path('/mnt/data/v3inspect/ngocc_v3/server.py')
s=p.read_text()
# imports
s=s.replace('import zipfile\n', 'import zipfile\nimport uuid\n')
# env constants after cloudinary folder
s=s.replace('CLOUDINARY_FOLDER = os.environ.get("NGOCC_CLOUDINARY_FOLDER", "ngocc_resources").strip("/")\n', 'CLOUDINARY_FOLDER = os.environ.get("NGOCC_CLOUDINARY_FOLDER", "ngocc_resources").strip("/")\nGITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()\nGITHUB_REPO = os.environ.get("GITHUB_REPO", "ngoccmod-stack/ngocc-skin-api").strip()\nCHUNK_DIR = UPLOADS / "resource_chunks"\nCHUNK_DIR.mkdir(parents=True, exist_ok=True)\n')
# replace cloudinary_ready to allow github storage? keep cloudinary for catalog if available
# Insert github helpers before resources upload endpoint
marker='@app.post("/api/resources/upload")\n'
insert=r'''
def github_headers():
    if not GITHUB_TOKEN:
        raise RuntimeError("Chưa cấu hình GITHUB_TOKEN trên Render.")
    return {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def github_create_or_get_release(version: str):
    h=github_headers(); base=f"https://api.github.com/repos/{GITHUB_REPO}"
    tag=f"resources-{version}"
    r=requests.get(f"{base}/releases/tags/{tag}",headers=h,timeout=30)
    if r.status_code==200: return r.json()
    if r.status_code!=404: r.raise_for_status()
    r=requests.post(f"{base}/releases",headers={**h,"Content-Type":"application/json"},json={"tag_name":tag,"name":f"Resources {version}","body":f"NGOCC Resources {version}","draft":False,"prerelease":False},timeout=30)
    r.raise_for_status(); return r.json()


def github_upload_asset(version: str, zip_path: Path):
    rel=github_create_or_get_release(version)
    # Remove old same-name asset if present.
    asset_name=f"Resources-{version}.zip"
    h=github_headers()
    for a in rel.get("assets",[]):
        if a.get("name")==asset_name:
            rr=requests.delete(a["url"],headers=h,timeout=30)
            if rr.status_code not in (204,404): rr.raise_for_status()
            break
    up_url=rel["upload_url"].split("{",1)[0] + "?name=" + asset_name
    with zip_path.open("rb") as fh:
        rr=requests.post(up_url,headers={**h,"Content-Type":"application/zip"},data=fh,timeout=1800)
    rr.raise_for_status()
    return rr.json()


def github_download_asset(asset_url: str, dest: Path):
    h={**github_headers(),"Accept":"application/octet-stream"}
    r=requests.get(asset_url,headers=h,timeout=1800,stream=True)
    r.raise_for_status()
    with dest.open("wb") as f:
        for ch in r.iter_content(1024*1024):
            if ch: f.write(ch)


@app.post("/api/resources/upload/init")
def resources_upload_init():
    sid=uuid.uuid4().hex
    (CHUNK_DIR/sid).mkdir(parents=True,exist_ok=True)
    return {"ok":True,"uploadId":sid,"chunkSize":8*1024*1024}


@app.post("/api/resources/upload/chunk")
async def resources_upload_chunk(uploadId: str, index: int, file: UploadFile = File(...)):
    d=CHUNK_DIR/uploadId
    if not d.is_dir(): raise HTTPException(404,"Upload session không tồn tại hoặc đã hết hạn.")
    target=d/f"{int(index):08d}.part"
    try:
        with target.open("wb") as f:
            while ch:=await file.read(1024*1024): f.write(ch)
        return {"ok":True,"index":int(index)}
    except Exception as e:
        raise HTTPException(500,f"Lưu chunk thất bại: {e}")


@app.post("/api/resources/upload/finalize")
def resources_upload_finalize(uploadId: str, total: int, filename: str):
    d=CHUNK_DIR/uploadId
    if not d.is_dir(): raise HTTPException(404,"Upload session không tồn tại.")
    try:
        safe=Path(filename).name
        if not safe.lower().endswith('.zip'): raise HTTPException(400,'Chỉ nhận Resources .zip')
        assembled=UPLOADS/f"assembled_{uploadId}.zip"
        with assembled.open('wb') as out:
            for i in range(int(total)):
                part=d/f"{i:08d}.part"
                if not part.is_file(): raise HTTPException(400,f"Thiếu phần {i+1}/{total}")
                with part.open('rb') as f: shutil.copyfileobj(f,out,1024*1024)
        # Validate and detect/install using the existing manager.
        cp=subprocess.run([sys.executable,str(AUTOMOD/'resource_manager.py'),'--resources',str(RESOURCES),'install',str(assembled)],cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
        if cp.returncode!=0: raise HTTPException(400,cp.stderr or cp.stdout or 'Không thể cài Resources')
        m=re.search(r'Installed Resources version:\s*(.+)',cp.stdout)
        version=m.group(1).strip() if m else ''
        if not version: raise HTTPException(400,'Không xác định được version Resources')
        asset=github_upload_asset(version,assembled)
        manifest=load_resource_manifest(); manifest.setdefault('versions',{})[version]={"version":version,"assetUrl":asset.get('url',''),"browserDownloadUrl":asset.get('browser_download_url',''),"releaseId":asset.get('id'),'uploadedAt':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),"size":assembled.stat().st_size}
        manifest['active']=version; save_resource_manifest(manifest); save_json(ACTIVE,{"version":version,"installedAt":__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()})
        return {"ok":True,"version":version,"stored":True,"size":assembled.stat().st_size}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500,f'Cập nhật Resources thất bại: {e}')
    finally:
        shutil.rmtree(d,ignore_errors=True); assembled.unlink(missing_ok=True)

'''
s=s.replace(marker, insert+marker)
# Change original upload endpoint to simply redirect to chunked-only message; safer not used by new frontend
start=s.index('@app.post("/api/resources/upload")\n')
end=s.index('\n@app.post("/api/scan")', start)
old=s[start:end]
new='''@app.post("/api/resources/upload")\nasync def upload_resources_legacy(file: UploadFile = File(...)):\n    raise HTTPException(400, "Hãy dùng giao diện upload Resources mới (chunked upload).")\n'''
s=s[:start]+new+s[end:]
# Change restore from cloud to github in ensure_local_resources_from_cloud body by replacing function entirely.
start=s.index('def ensure_local_resources_from_cloud')
end=s.index('\n\n@app.get("/api/resources/status")', start)
func=r'''def ensure_local_resources_from_cloud(version: str | None = None) -> str:
    versions = find_resource_versions(RESOURCES)
    if version:
        local=RESOURCES/version
        if (local/"Databin/Client/Actor/heroSkin.bytes").is_file(): return version
    elif versions:
        return versions[-1].name
    manifest=load_resource_manifest(); target=version or manifest.get('active') or ''
    if not target: raise FileNotFoundError('Chưa có Resources; Admin hãy cập nhật Resources trước.')
    info=manifest.get('versions',{}).get(target) or {}
    asset_url=info.get('assetUrl')
    if not asset_url:
        # Try resolving from release tag.
        if not GITHUB_TOKEN: raise FileNotFoundError('Chưa có GITHUB_TOKEN để khôi phục Resources.')
        h=github_headers(); base=f'https://api.github.com/repos/{GITHUB_REPO}/releases/tags/resources-{target}'
        r=requests.get(base,headers=h,timeout=30); r.raise_for_status(); rel=r.json();
        asset=next((a for a in rel.get('assets',[]) if a.get('name')==f'Resources-{target}.zip'),None)
        if not asset: raise FileNotFoundError(f'Không tìm thấy Resources {target} trong GitHub Release.')
        asset_url=asset['url']
    local_zip=UPLOADS/f'restore_{target}.zip'
    try:
        github_download_asset(asset_url,local_zip)
        cp=subprocess.run([sys.executable,str(AUTOMOD/'resource_manager.py'),'--resources',str(RESOURCES),'install',str(local_zip)],cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
        if cp.returncode!=0: raise RuntimeError(cp.stderr or cp.stdout or 'Không thể khôi phục Resources')
        m=re.search(r'Installed Resources version:\s*(.+)',cp.stdout)
        return m.group(1).strip() if m else target
    finally: local_zip.unlink(missing_ok=True)
'''
s=s[:start]+func+s[end:]
p.write_text(s)

# frontend replace uploader function
hp=Path('/mnt/data/v3inspect/ngocc_v3/web/index.html')
h=hp.read_text()
start=h.index('window.uploadSkinResources=function(input){')
end=h.index('\n\n</script>', start)
newjs=r'''window.uploadSkinResources=async function(input){
  if(typeof isOwner==='function' && !isOwner()) return;
  const file=input?.files?.[0]; if(!file) return;
  if(!/\.zip$/i.test(file.name)){ alert('Vui lòng chọn file Resources .zip'); input.value=''; return; }
  const status=document.getElementById('skinAdminStatus');
  const api=skinApiUrl('');
  const chunkSize=8*1024*1024;
  try{
    status.textContent='⏳ Đang chuẩn bị upload Resources...';
    const init=await fetch(api+'/api/resources/upload/init',{method:'POST'});
    const initData=await init.json(); if(!init.ok) throw new Error(initData.detail||('HTTP '+init.status));
    const uploadId=initData.uploadId; const total=Math.ceil(file.size/chunkSize);
    for(let i=0;i<total;i++){
      const blob=file.slice(i*chunkSize,Math.min(file.size,(i+1)*chunkSize));
      const fd=new FormData(); fd.append('file',blob,file.name+'.part'+i);
      fd.append('uploadId',uploadId); fd.append('index',String(i));
      let ok=false;
      for(let retry=0;retry<3 && !ok;retry++){
        try{
          const r=await fetch(api+'/api/resources/upload/chunk?uploadId='+encodeURIComponent(uploadId)+'&index='+i,{method:'POST',body:fd});
          const d=await r.json().catch(()=>({})); if(!r.ok) throw new Error(d.detail||('HTTP '+r.status)); ok=true;
        }catch(e){ if(retry===2) throw e; await new Promise(res=>setTimeout(res,1000*(retry+1))); }
      }
      status.textContent=`⏳ Đang tải Resources: ${Math.round((i+1)/total*100)}% • phần ${i+1}/${total}`;
    }
    status.textContent='⏳ Đang ghép + cài Resources...';
    const r=await fetch(api+'/api/resources/upload/finalize?uploadId='+encodeURIComponent(uploadId)+'&total='+total+'&filename='+encodeURIComponent(file.name),{method:'POST'});
    const d=await r.json().catch(()=>({})); if(!r.ok) throw new Error(d.detail||('HTTP '+r.status));
    status.textContent=`✅ Resources ${d.version||''} đã cập nhật. Bấm “Quét” để cập nhật catalog.`;
  }catch(e){ console.error(e); status.textContent='❌ '+(e.message||'Upload thất bại'); }
  finally{ input.value=''; }
};'''
h=h[:start]+newjs+h[end:]
hp.write_text(h)
