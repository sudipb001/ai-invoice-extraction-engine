from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"success": False, "error": "Only PDF files allowed"}

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = UPLOAD_DIR / filename

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "filename": filename
    }
