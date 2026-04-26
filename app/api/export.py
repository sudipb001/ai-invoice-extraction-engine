from fastapi import APIRouter
from pathlib import Path
import pandas as pd

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
EXPORT_DIR = Path("exports")

EXPORT_DIR.mkdir(exist_ok=True)

@router.get("/export/{filename}")
def export_invoice(filename: str):
    path = UPLOAD_DIR / filename

    extracted = extract_text_from_pdf(str(path))

    if not extracted["success"]:
        return extracted

    parsed = parse_invoice_text(extracted["text"])

    if not parsed["success"]:
        return parsed

    df = pd.DataFrame([parsed["data"]])

    export_name = filename.replace(".pdf", ".xlsx")
    export_path = EXPORT_DIR / export_name

    df.to_excel(export_path, index=False)

    return {
        "success": True,
        "file": export_name
    }
