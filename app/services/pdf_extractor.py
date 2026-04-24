import pdfplumber
from pathlib import Path


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
            return {
                "success": False,
                "error": "No readable text found. PDF may be scanned or blank.",
                "pages": total_pages
            }

        return {
            "success": True,
            "pages": total_pages,
            "text": full_text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
