import streamlit as st
from pathlib import Path
import uuid

from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 10

st.set_page_config(
    page_title="AI Invoice Extraction Engine",
    layout="wide"
)

st.title("AI Invoice Extraction Engine")
st.subheader("Upload and Parse Invoices")

uploaded_file = st.file_uploader(
    "Upload Invoice PDF",
    type=["pdf"]
)

saved_file = None

if uploaded_file is not None:
    size_mb = uploaded_file.size / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        st.error("File too large.")
    else:
        filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        path = UPLOAD_DIR / filename

        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        saved_file = path
        st.success("File uploaded successfully.")

if saved_file:

    if st.button("Extract Text"):
        result = extract_text_from_pdf(str(saved_file))

        if result["success"]:
            st.text_area(
                "Extracted Text",
                result["text"],
                height=300
            )
        else:
            st.error(result["error"])

    if st.button("Parse Invoice"):
        extracted = extract_text_from_pdf(str(saved_file))

        if extracted["success"]:
            parsed = parse_invoice_text(extracted["text"])

            if parsed["success"]:
                st.success("Invoice parsed successfully.")
                st.json(parsed["data"])
            else:
                st.error(parsed["error"])
        else:
            st.error(extracted["error"])
