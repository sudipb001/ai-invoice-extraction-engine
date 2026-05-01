import streamlit as st
import uuid
import requests
from pathlib import Path


from app.config import UPLOAD_DIR, MAX_FILE_SIZE_MB, MAX_BATCH_SIZE, BATCH_INTER_FILE_DELAY
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

if "batch_results" not in st.session_state:
    st.session_state.batch_results = []

if "batch_export_path" not in st.session_state:
    st.session_state.batch_export_path = None

if "ocr_used" not in st.session_state:
    st.session_state.ocr_used = None

if "is_duplicate" not in st.session_state:
    st.session_state.is_duplicate = None

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
tab1, tab2, tab3 = st.tabs(["Process Invoice", "Batch Processing", "History"])


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
            st.session_state.ocr_used = result.get("ocr_used", False)
            st.success("Text extracted successfully.")
            if st.session_state.get("ocr_used"):
                st.info("OCR was used (scanned PDF detected).")
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
            st.session_state.is_duplicate = parsed.get("duplicate", False)
            st.success("Invoice parsed successfully.")
            if st.session_state.get("is_duplicate"):
                st.warning("Duplicate invoice detected.")
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
        st.session_state.ocr_used = None
        st.session_state.is_duplicate = None
        st.rerun()


# =======================================
# TAB 2 — BATCH PROCESSING
# =======================================
with tab2:

    st.subheader("Batch Invoice Processing")

    uploaded_files = st.file_uploader(
        "Upload Multiple Invoice PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        if len(uploaded_files) > MAX_BATCH_SIZE:
            st.error(f"Maximum {MAX_BATCH_SIZE} files allowed.")
        else:

            if st.button("Start Batch Processing"):

                st.session_state.batch_results = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                total_files = len(uploaded_files)

                for i, file in enumerate(uploaded_files):

                    status_text.text(f"Processing {i+1}/{total_files}: {file.name}")

                    try:
                        # Save file
                        filename = f"{uuid.uuid4()}_{file.name}"
                        path = UPLOAD_DIR / filename

                        with open(path, "wb") as f:
                            f.write(file.getbuffer())

                        # Extract text
                        extracted = extract_text_from_pdf(str(path))

                        if not extracted["success"]:
                            st.session_state.batch_results.append({
                                "filename": file.name,
                                "success": False,
                                "error": extracted["error"]
                            })
                            continue

                        # Parse invoice
                        parsed = parse_invoice_text(extracted["text"])

                        if not parsed["success"]:
                            st.session_state.batch_results.append({
                                "filename": file.name,
                                "success": False,
                                "error": parsed["error"]
                            })
                            continue

                        # Success case
                        st.session_state.batch_results.append({
                            "filename": file.name,
                            "success": True,
                            "data": parsed["data"]
                        })

                    except Exception as e:
                        st.session_state.batch_results.append({
                            "filename": file.name,
                            "success": False,
                            "error": str(e)
                        })

                    # Progress update
                    progress_bar.progress((i + 1) / total_files)

                    # Rate limit protection
                    import time
                    time.sleep(BATCH_INTER_FILE_DELAY)

                status_text.text("Batch processing completed.")
                st.success("Batch processing finished.")

    # ===================================
    # RESULTS TABLE
    # ===================================
    if st.session_state.batch_results:

        st.subheader("Batch Results")

        results_display = []

        for item in st.session_state.batch_results:
            results_display.append({
                "File": item["filename"],
                "Status": "Success" if item["success"] else "Failed",
                "Error": item.get("error", "")
            })

        st.table(results_display)

        # ===================================
        # EXPORT SECTION
        # ===================================
        success_data = [
            item["data"]
            for item in st.session_state.batch_results
            if item["success"]
        ]

        if success_data:

            from app.services.export_service import (
                build_dataframe,
                export_excel,
                export_csv,
                generate_filename
            )

            export_format = st.selectbox(
                "Export Format",
                ["excel", "csv"],
                key="batch_export_format"
            )

            if st.button("Export Batch Report"):

                df = build_dataframe(success_data)

                if export_format == "excel":
                    filename = generate_filename("batch", "xlsx")
                    file_path = export_excel(df, filename)
                else:
                    filename = generate_filename("batch", "csv")
                    file_path = export_csv(df, filename)

                st.session_state.batch_export_path = str(file_path)

                st.success("Batch export created.")

        # Download button
        if st.session_state.batch_export_path:
            with open(st.session_state.batch_export_path, "rb") as f:
                st.download_button(
                    label="Download Batch File",
                    data=f,
                    file_name=Path(st.session_state.batch_export_path).name
                )

        # ===================================
        # RESET BUTTON
        # ===================================
        if st.button("Reset Batch"):
            st.session_state.batch_results = []
            st.session_state.batch_export_path = None
            st.rerun()



# =======================================
# TAB 3 — HISTORY
# =======================================
with tab3:


    st.subheader("System History")


    col1, col2 = st.columns(2)


    with col1:
        st.write("Uploaded Files")
        st.table(history_data.get("uploaded_files", []))


    with col2:
        st.write("Exported Files")
        st.table(history_data.get("exported_files", []))