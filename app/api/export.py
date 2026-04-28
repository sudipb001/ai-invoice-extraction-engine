from fastapi import APIRouter, HTTPException
import pandas as pd

from app.config import UPLOAD_DIR, EXPORT_DIR
from app.utils.file_utils import safe_upload_path
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

router = APIRouter()


@router.get("/export/{filename}")
def export_invoice(filename: str):
    path = safe_upload_path(UPLOAD_DIR, filename)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    extracted = extract_text_from_pdf(str(path))

    if not extracted["success"]:
        raise HTTPException(
            status_code=422,
            detail=extracted["error"]
        )

    parsed = parse_invoice_text(extracted["text"])

    if not parsed["success"]:
        raise HTTPException(
            status_code=503,
            detail=parsed["error"]
        )

    try:
        df = pd.DataFrame([parsed["data"]])

        export_name = filename.replace(".pdf", ".xlsx")
        export_path = EXPORT_DIR / export_name

        df.to_excel(export_path, index=False)

        return {
            "success": True,
            "file": export_name
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Excel export failed."
        )
