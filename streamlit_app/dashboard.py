import streamlit as st
from pathlib import Path
import uuid

from app.services.pdf_extractor import extract_text_from_pdf

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 10

st.set_page_config(
    page_title="AI Invoice Extraction Engine",
    layout="wide"
)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload Invoice PDF",
        type=["pdf"]
    )

with col2:
    st.metric("Max Size", "10 MB")
    st.metric("Allowed Type", "PDF")


saved_file = None

if uploaded_file is not None:
    size_mb = uploaded_file.size / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        st.error("File too large")
    else:
        filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        save_path = UPLOAD_DIR / filename

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        saved_file = save_path
        st.success("File uploaded successfully")

if saved_file:
    if st.button("Extract Text"):
        result = extract_text_from_pdf(str(saved_file))

        if result["success"]:
            st.success("Text extracted successfully")
            st.write(f"Pages: {result['pages']}")
            st.text_area(
                "Extracted Text",
                result["text"],
                height=400
            )
        else:
            st.error(result["error"])

