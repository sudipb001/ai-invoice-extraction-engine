from fastapi import APIRouter
from pathlib import Path

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")

@router.get("/parse/{filename}")
def parse_invoice(filename: str):
    path = UPLOAD_DIR / filename

    extracted = extract_text_from_pdf(str(path))

    if not extracted["success"]:
        return extracted

    return parse_invoice_text(extracted["text"])
