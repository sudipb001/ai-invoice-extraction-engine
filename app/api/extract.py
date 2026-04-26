from fastapi import APIRouter
from pathlib import Path

from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter()

UPLOAD_DIR = Path("uploads")

@router.get("/extract/{filename}")
def extract_invoice(filename: str):
    path = UPLOAD_DIR / filename
    return extract_text_from_pdf(str(path))
    