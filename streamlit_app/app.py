import streamlit as st
from pathlib import Path
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 10

st.set_page_config(
    page_title="AI Invoice Extraction Engine",
    layout="wide"
)

st.title("AI Invoice Extraction Engine")
st.subheader("Upload Invoice PDFs")
st.write("Upload invoice PDF files for AI-based extraction.")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload Invoice PDF",
        type=["pdf"]
    )

with col2:
    st.metric("Max Size", "10 MB")
    st.metric("Allowed Type", "PDF")


if uploaded_file is not None:

    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"File exceeds {MAX_FILE_SIZE_MB} MB limit.")
    else:
        unique_name = f"{uuid.uuid4()}_{uploaded_file.name}"
        save_path = UPLOAD_DIR / unique_name

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Invoice uploaded successfully.")
        st.info(f"Saved as: {unique_name}")
        file_size_bytes = uploaded_file.size
        file_size_kb = file_size_bytes / 1024
        file_size_mb = file_size_kb / 1024

        if file_size_mb >= 1:
            st.write(f"Size: {file_size_mb:.2f} MB")
        else:
            st.write(f"Size: {file_size_kb:.2f} KB")
