from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

app = FastAPI(title="AI Invoice Extraction Engine")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {"message": "API Running Successfully"}

@app.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files allowed"}

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = UPLOAD_DIR / filename

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "filename": filename
    }

@app.get("/extract/{filename}")
def extract_invoice(filename: str):
    path = UPLOAD_DIR / filename
    return extract_text_from_pdf(str(path))

@app.get("/parse/{filename}")
def parse_invoice(filename: str):
    path = UPLOAD_DIR / filename

    extracted = extract_text_from_pdf(str(path))

    if not extracted["success"]:
        return extracted

    return parse_invoice_text(extracted["text"])
