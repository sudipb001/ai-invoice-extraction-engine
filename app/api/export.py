from fastapi import APIRouter, HTTPException
import pandas as pd
from fastapi import Query

from app.services.export_service import (
    build_dataframe,
    export_excel,
    export_csv,
    generate_filename
)


from app.config import UPLOAD_DIR, EXPORT_DIR
from app.utils.file_utils import safe_upload_path
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

router = APIRouter()


@router.get("/export/{filename}")
def export_invoice(
    filename: str,
    format: str = Query("excel", enum=["excel", "csv"])
):
    path = safe_upload_path(UPLOAD_DIR, filename)

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    extracted = extract_text_from_pdf(str(path))

    if not extracted["success"]:
        raise HTTPException(status_code=422, detail=extracted["error"])

    parsed = parse_invoice_text(extracted["text"])

    if not parsed["success"]:
        raise HTTPException(status_code=503, detail=parsed["error"])

    try:
        df = build_dataframe([parsed["data"]])

        if format == "excel":
            name = generate_filename(filename, "xlsx")
            file_path = export_excel(df, name)
        else:
            name = generate_filename(filename, "csv")
            file_path = export_csv(df, name)

        return {
            "success": True,
            "file": name,
            "path": str(file_path)
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Export failed.")

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


@router.post("/export/batch")
def export_batch(
    filenames: list[str],
    format: str = Query("excel", enum=["excel", "csv"])
):
    results = []

    for name in filenames:
        path = safe_upload_path(UPLOAD_DIR, name)

        if not path.exists():
            continue

        extracted = extract_text_from_pdf(str(path))
        if not extracted["success"]:
            continue

        parsed = parse_invoice_text(extracted["text"])
        if not parsed["success"]:
            continue

        results.append(parsed["data"])

    if not results:
        raise HTTPException(status_code=400, detail="No valid data.")

    df = build_dataframe(results)

    filename = generate_filename("batch", "xlsx" if format == "excel" else "csv")

    if format == "excel":
        file_path = export_excel(df, filename)
    else:
        file_path = export_csv(df, filename)

    return {
        "success": True,
        "file": filename
    }
