from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

# Windows users must set this path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_with_ocr(file_path: str) -> str:
    try:

        images = convert_from_path(file_path)

        text_pages = []

        for img in images:
            text = pytesseract.image_to_string(img)

            if text:
                text_pages.append(text)

        return "\n\n".join(text_pages)

    except Exception:
        return ""
