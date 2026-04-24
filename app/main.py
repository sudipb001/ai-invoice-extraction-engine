from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid

from app.services.pdf_extractor import extract_text_from_pdf

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

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    save_path = UPLOAD_DIR / unique_name

    content = await file.read()

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "message": "Upload successful",
        "filename": unique_name
    }


@app.get("/extract/{filename}")
def extract_invoice(filename: str):
    file_path = UPLOAD_DIR / filename
    return extract_text_from_pdf(str(file_path))
