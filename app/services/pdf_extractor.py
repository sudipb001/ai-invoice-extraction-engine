import pdfplumber
from pathlib import Path
from app.services.ocr_extractor import extract_text_with_ocr


def clean_text(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned)


def extract_text_from_pdf(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "error": "File not found"
        }

    try:
        all_pages = []
        total_pages = 0

        with pdfplumber.open(path) as pdf:
            total_pages = len(pdf.pages)

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_pages.append(text)

        full_text = "\n\n".join(all_pages)
        full_text = clean_text(full_text)

        if not full_text:

            ocr_text = extract_text_with_ocr(str(path))

            if ocr_text:
                return {
                    "success": True,
                    "pages": total_pages,
                    "text": clean_text(ocr_text),
                    "ocr_used": True
                }

            return {
                "success": False,
                "error": "No readable text found.",
                "pages": total_pages
            }


        return {
            "success": True,
            "pages": total_pages,
            "text": full_text,
            "ocr_used": False
        }


    except Exception:
        return {
            "success": False,
            "error": "Unable to read PDF file."
        }

