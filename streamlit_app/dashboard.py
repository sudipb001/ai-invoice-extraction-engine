import streamlit as st
import uuid

from app.config import UPLOAD_DIR, MAX_FILE_SIZE_MB
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text

st.set_page_config(
    page_title="AI Invoice Extraction Engine",
    layout="wide"
)

st.title("AI Invoice Extraction Engine")
st.subheader("Reliable Invoice Processing")

if "saved_file" not in st.session_state:
    st.session_state.saved_file = None

uploaded_file = st.file_uploader(
    "Upload Invoice PDF",
    type=["pdf"]
)

if uploaded_file is not None and st.session_state.saved_file is None:
    size_mb = uploaded_file.size / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        st.error("File too large.")
    else:
        filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        path = UPLOAD_DIR / filename

        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.saved_file = str(path)
        st.success("File uploaded successfully.")

if st.session_state.saved_file:

    if st.button("Extract Text"):
        result = extract_text_from_pdf(
            st.session_state.saved_file
        )

        if result["success"]:
            st.text_area(
                "Extracted Text",
                result["text"],
                height=350
            )
        else:
            st.error(result["error"])

    if st.button("Parse Invoice"):
        extracted = extract_text_from_pdf(
            st.session_state.saved_file
        )

        if extracted["success"]:
            parsed = parse_invoice_text(
                extracted["text"]
            )

            if parsed["success"]:
                st.json(parsed["data"])
            else:
                st.error(parsed["error"])
        else:
            st.error(extracted["error"])

    if st.button("Reset"):
        st.session_state.saved_file = None
        st.rerun()
