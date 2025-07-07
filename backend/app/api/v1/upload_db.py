from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import shutil
import os

router = APIRouter()

@router.post("/upload-db/")
async def upload_db(
    file: UploadFile = File(...),
    token: str = Header(None)
):
    expected_token = os.getenv("UPLOAD_DB_TOKEN")
    if not expected_token or token != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_path = "/backend/data/personalfinance.db"
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"} 