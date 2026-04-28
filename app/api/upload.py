from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid

from app.config import UPLOAD_DIR, MAX_FILE_SIZE_BYTES
from app.utils.file_utils import sanitize_filename

router = APIRouter()


@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    original_name = sanitize_filename(file.filename)

    if not original_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File exceeds allowed size."
        )

    filename = f"{uuid.uuid4()}_{original_name}"
    save_path = UPLOAD_DIR / filename

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "filename": filename
    }
