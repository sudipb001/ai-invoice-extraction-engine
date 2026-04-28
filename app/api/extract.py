from fastapi import APIRouter, HTTPException

from app.config import UPLOAD_DIR
from app.services.pdf_extractor import extract_text_from_pdf
from app.utils.file_utils import safe_upload_path

router = APIRouter()


@router.get("/extract/{filename}")
def extract_invoice(filename: str):
    path = safe_upload_path(UPLOAD_DIR, filename)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    result = extract_text_from_pdf(str(path))

    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=result["error"]
        )

    return result
