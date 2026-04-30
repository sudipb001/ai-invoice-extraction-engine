import streamlit as st
import uuid
import requests
from pathlib import Path


from app.config import UPLOAD_DIR, MAX_FILE_SIZE_MB
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.ai_parser import parse_invoice_text


API_BASE = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Invoice Extraction Engine",
    layout="wide"
)


st.title("AI Invoice Extraction Engine")


# ---------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------
if "saved_file" not in st.session_state:
    st.session_state.saved_file = None


if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None


if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None


if "export_file_path" not in st.session_state:
    st.session_state.export_file_path = None


# ---------------------------------------
# LOAD HISTORY DATA
# ---------------------------------------
def load_history():
    try:
        response = requests.get(f"{API_BASE}/history")
        if response.status_code == 200:
            return response.json()
    except:
        return {"uploaded_files": [], "exported_files": []}


history_data = load_history()


uploads_count = len(history_data.get("uploaded_files", []))
exports_count = len(history_data.get("exported_files", []))
current_file = (
    Path(st.session_state.saved_file).name
    if st.session_state.saved_file else "None"
)


# ---------------------------------------
# KPI CARDS
# ---------------------------------------
col1, col2, col3 = st.columns(3)


col1.metric("Total Uploads", uploads_count)
col2.metric("Total Exports", exports_count)
col3.metric("Current File", current_file)


st.divider()


# ---------------------------------------
# TABS
# ---------------------------------------
tab1, tab2 = st.tabs(["Process Invoice", "History"])


# =======================================
# TAB 1 — PROCESS INVOICE
# =======================================
with tab1:


    st.subheader("Upload Invoice")


    uploaded_file = st.file_uploader(
        "Upload Invoice PDF",
        type=["pdf"]
    )


    if uploaded_file is not None and st.session_state.saved_file is None:
        size_mb = uploaded_file.size / (1024 * 1024)


        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File exceeds {MAX_FILE_SIZE_MB} MB limit.")
        else:
            filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            path = UPLOAD_DIR / filename


            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            st.session_state.saved_file = str(path)
            st.success("File uploaded successfully.")


    st.divider()


    # ---------------------------
    # EXTRACT SECTION
    # ---------------------------
    st.subheader("Extract Text")


    if st.button("Extract Text", disabled=not st.session_state.saved_file):


        with st.spinner("Extracting text from PDF..."):
            result = extract_text_from_pdf(
                st.session_state.saved_file
            )


        if result["success"]:
            st.session_state.extracted_text = result["text"]
            st.success("Text extracted successfully.")
        else:
            st.error(result["error"])


    if st.session_state.extracted_text:
        with st.expander("View Extracted Text"):
            st.text_area(
                "Extracted Text",
                st.session_state.extracted_text,
                height=300
            )


    st.divider()


    # ---------------------------
    # PARSE SECTION
    # ---------------------------
    st.subheader("Parse Invoice")


    if st.button(
        "Parse Invoice",
        disabled=not st.session_state.extracted_text
    ):
        with st.spinner("Parsing invoice using AI..."):
            parsed = parse_invoice_text(
                st.session_state.extracted_text
            )


        if parsed["success"]:
            st.session_state.parsed_data = parsed["data"]
            st.success("Invoice parsed successfully.")
        else:
            st.error(parsed["error"])


    if st.session_state.parsed_data:
        st.subheader("Parsed Invoice Data")
        st.json(st.session_state.parsed_data)


    st.divider()


    # ---------------------------
    # EXPORT SECTION
    # ---------------------------
    st.subheader("Export")


    export_format = st.selectbox("Format", ["excel", "csv"])


    if st.button(
        "Export Invoice",
        disabled=not st.session_state.parsed_data
    ):
        filename = Path(st.session_state.saved_file).name


        with st.spinner("Generating export file..."):
            response = requests.get(
                f"{API_BASE}/export/{filename}",
                params={"format": export_format}
            )


        if response.status_code == 200:
            data = response.json()
            st.session_state.export_file_path = data["path"]
            st.success("Export generated successfully.")
        else:
            st.error("Export failed.")


    if st.session_state.export_file_path:
        with open(st.session_state.export_file_path, "rb") as f:
            st.download_button(
                label="Download File",
                data=f,
                file_name=Path(st.session_state.export_file_path).name,
                mime="application/octet-stream"
            )


    st.divider()


    # ---------------------------
    # RESET
    # ---------------------------
    if st.button("Reset"):
        st.session_state.saved_file = None
        st.session_state.extracted_text = None
        st.session_state.parsed_data = None
        st.session_state.export_file_path = None
        st.rerun()


# =======================================
# TAB 2 — HISTORY
# =======================================
with tab2:


    st.subheader("System History")


    col1, col2 = st.columns(2)


    with col1:
        st.write("Uploaded Files")
        st.table(history_data.get("uploaded_files", []))


    with col2:
        st.write("Exported Files")
        st.table(history_data.get("exported_files", []))