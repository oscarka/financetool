from fastapi import APIRouter, UploadFile, File
import shutil
import os

router = APIRouter()

@router.post("/upload-db/")
async def upload_db(file: UploadFile = File(...)):
    db_path = "/backend/data/personalfinance.db"
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "uploaded"} 