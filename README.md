# AI Invoice Extraction Engine

## Overview

The AI Invoice Extraction Engine is a production-grade, AI-powered document processing system that automates the extraction of structured data from PDF invoices. It combines traditional text extraction, OCR fallback, and large language model parsing into a single, cohesive pipeline exposed through a FastAPI backend and a Streamlit dashboard.

Manual invoice processing is time-consuming, error-prone, and difficult to scale. Accounts payable teams, small and medium enterprises, freelancers, and finance departments routinely handle large volumes of PDF invoices in varying formats. This system eliminates the need for manual data entry by extracting key invoice fields automatically, validating the results, detecting duplicates, normalising currencies, and exporting the structured data in Excel or CSV format.

**Target users:** Accounts payable teams, bookkeepers, SME finance departments, freelancers managing client invoices, and developers building document automation workflows.

---

## Key Features

- **PDF upload with validation** — Accepts only `.pdf` files up to 10 MB; filenames are sanitised and stored with a UUID prefix to prevent collisions and path traversal.
- **Multi-page text extraction** — Uses pdfplumber to extract text from every page of a PDF, with page count reporting.
- **OCR fallback for scanned PDFs** — When pdfplumber yields no usable text, the system converts pages to images via pdf2image and runs Tesseract OCR automatically.
- **AI-based structured invoice parsing** — Sends extracted text to OpenAI `gpt-4o-mini` with a structured prompt; the response is parsed into a validated Pydantic model.
- **JSON validation with Pydantic** — All extracted fields are validated against a typed schema before any downstream processing or export.
- **Excel and CSV export** — Exports single or batch invoices with human-readable column headers; Excel output includes bold headers and auto-adjusted column widths.
- **Batch invoice processing** — Accepts up to 50 files in a single batch operation with a configurable inter-file delay to manage API rate limits.
- **Duplicate invoice detection** — Identifies duplicates based on a composite key of invoice number, vendor name, and total amount against a rolling history of 1,000 processed invoices.
- **Currency normalisation** — Converts currency symbols (`$`, `€`, `£`, `₹`, `¥`, `Rs`) to ISO 4217 codes (USD, EUR, GBP, INR, JPY) during parsing.
- **Streamlit dashboard UI** — Browser-based interface for single invoice processing, batch processing, and history review.
- **History tracking** — Lists all uploaded and exported files via a dedicated API endpoint.
- **Error handling and retries** — OpenAI calls retry up to 2 times with exponential backoff; all API errors return structured JSON responses with appropriate HTTP status codes.

---

## System Architecture

The system is composed of three layers:

**1. Presentation Layer — Streamlit**
A browser-based dashboard (`streamlit_app/dashboard.py`) provides a tabbed interface for uploading invoices, running the extraction and parsing pipeline, reviewing parsed data, exporting results, and viewing processing history. It communicates with the FastAPI backend over HTTP.

**2. API Layer — FastAPI**
The backend (`app/api/`) exposes RESTful endpoints for upload, extraction, parsing, export, and history. Each endpoint performs input validation, delegates to the service layer, and returns structured JSON responses.

**3. Service Layer — Business Logic**
The `app/services/` directory contains the core processing components: PDF text extraction (`pdf_extractor.py`), OCR fallback (`ocr_extractor.py`), AI parsing (`ai_parser.py`), currency normalisation (`currency_normalizer.py`), duplicate detection (`duplicate_detector.py`), and export generation (`export_service.py`).

**Data flow:**

```
User (Browser)
    │
    ▼
Streamlit Dashboard
    │  HTTP
    ▼
FastAPI Backend
    │
    ├── /upload       → Validate + store PDF
    ├── /extract      → pdfplumber → OCR fallback → raw text
    ├── /parse        → AI parsing → Pydantic validation → duplicate check
    └── /export       → DataFrame → Excel / CSV
```

Extracted invoice data is not persisted in a database between steps. The parse endpoint re-runs the full extraction and AI parsing pipeline on demand. Export reads parsed data from the same pipeline and writes the result to the `exports/` directory. Duplicate detection state is maintained in a lightweight JSON file (`data/processed_invoices.json`).

---

## Folder Structure

```
ai-invoice-extraction-engine/
│
├── main.py                        # Project entry point (development placeholder)
├── pyproject.toml                 # Project metadata and dependencies (uv)
├── .env                           # Environment variables (not committed)
│
├── app/
│   ├── main.py                    # FastAPI application factory and router registration
│   ├── config.py                  # Centralised configuration (paths, limits, timeouts)
│   │
│   ├── api/
│   │   ├── upload.py              # POST /upload
│   │   ├── extract.py             # GET /extract/{filename}
│   │   ├── parse.py               # GET /parse/{filename}
│   │   ├── export.py              # GET /export/{filename}, POST /export/batch
│   │   └── history.py             # GET /history
│   │
│   ├── models/
│   │   └── invoice.py             # InvoiceData Pydantic model
│   │
│   ├── services/
│   │   ├── ai_parser.py           # OpenAI gpt-4o-mini invoice parsing
│   │   ├── ocr_extractor.py       # Tesseract OCR via pdf2image
│   │   ├── pdf_extractor.py       # pdfplumber text extraction with OCR fallback
│   │   ├── currency_normalizer.py # Symbol-to-ISO-code currency normalisation
│   │   ├── duplicate_detector.py  # JSON-backed duplicate detection
│   │   └── export_service.py      # pandas DataFrame + Excel/CSV generation
│   │
│   └── utils/
│       ├── file_utils.py          # Filename sanitisation and path traversal protection
│       └── file_store.py          # JSON file load/save utilities
│
├── streamlit_app/
│   └── dashboard.py               # Streamlit UI (tabs: Process, Batch, History)
│
├── uploads/                       # Uploaded PDF files (UUID-prefixed)
├── exports/                       # Generated Excel and CSV files
└── data/                          # processed_invoices.json (duplicate detection state)
```

---

## Installation and Setup

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows) or available on `PATH` (Linux/macOS)
- An OpenAI API key

### Step 1 — Install uv

```bash
pip install uv
```

### Step 2 — Clone the repository

```bash
git clone https://github.com/your-username/ai-invoice-extraction-engine.git
cd ai-invoice-extraction-engine
```

### Step 3 — Create a virtual environment

```bash
uv venv
```

### Step 4 — Activate the virtual environment

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### Step 5 — Install dependencies

```bash
uv sync
```

### Step 6 — Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

The application loads this file automatically via `python-dotenv`.

### Step 7 — Verify directory structure

The following directories must exist before running the application. Create them if absent:

```bash
mkdir uploads exports data
```

---

## Running the Application

### Start the FastAPI backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### Start the Streamlit dashboard

In a separate terminal (with the virtual environment activated):

```bash
streamlit run streamlit_app/dashboard.py
```

The dashboard will be available at: `http://localhost:8501`

The Streamlit application connects to the FastAPI backend at `http://127.0.0.1:8000`. Both processes must be running simultaneously for the full system to function.

---

## API Endpoints

### `POST /upload`

Accepts a multipart form file upload. Validates that the file is a PDF, is non-empty, has a sanitised filename matching `^[A-Za-z0-9._-]+$`, and does not exceed 10 MB. The file is saved to the `uploads/` directory with a UUID prefix.

**Request:** `multipart/form-data` with field `file`

**Response:**

```json
{
  "success": true,
  "filename": "a1b2c3d4-uuid_invoice.pdf"
}
```

---

### `GET /extract/{filename}`

Extracts raw text from an uploaded PDF using pdfplumber. If no text is found (indicating a scanned document), the system automatically falls back to Tesseract OCR. The response includes page count, extracted text, and a flag indicating whether OCR was used.

**Response:**

```json
{
  "success": true,
  "pages": 2,
  "text": "INVOICE\nVendor: Acme Corp\n...",
  "ocr_used": false
}
```

---

### `GET /parse/{filename}`

Runs the full processing pipeline: text extraction, OpenAI `gpt-4o-mini` parsing, Pydantic validation, currency normalisation, and duplicate detection. Returns the structured invoice data and a duplicate flag.

**Response:**

```json
{
  "success": true,
  "data": {
    "invoice_number": "INV-2024-001",
    "vendor_name": "Acme Corporation",
    "invoice_date": "2024-01-15",
    "due_date": "2024-02-15",
    "tax_amount": 150.0,
    "total_amount": 1650.0,
    "currency": "USD"
  },
  "duplicate": false
}
```

---

### `GET /export/{filename}?format=excel`

Parses the specified invoice and exports the result to a file. Accepts a `format` query parameter of either `excel` or `csv`. The generated file is saved to the `exports/` directory with a timestamped filename.

**Query parameters:** `format` — `excel` (default) or `csv`

**Response:**

```json
{
  "success": true,
  "file": "a1b2c3d4_invoice_20260503_120000.xlsx",
  "path": "./exports/a1b2c3d4_invoice_20260503_120000.xlsx"
}
```

---

### `POST /export/batch`

Accepts a list of filenames and exports all parseable invoices into a single consolidated file. Files that fail extraction or parsing are skipped. Supports the same `format` query parameter as single export.

**Query parameters:** `format` — `excel` or `csv`

**Request body:**

```json
{
  "filenames": ["uuid1_invoice_a.pdf", "uuid2_invoice_b.pdf"]
}
```

**Response:**

```json
{
  "success": true,
  "file": "batch_20260503_120000.xlsx"
}
```

---

### `GET /history`

Returns a list of all filenames currently present in the `uploads/` and `exports/` directories.

**Response:**

```json
{
  "success": true,
  "uploaded_files": ["uuid1_invoice_a.pdf", "uuid2_invoice_b.pdf"],
  "exported_files": ["batch_20260503_120000.xlsx"]
}
```

---

## Usage Guide

### Single Invoice — End-to-End Workflow

**Step 1 — Upload an invoice**

Open the Streamlit dashboard at `http://localhost:8501`. Select the "Process Invoice" tab and use the file uploader to select a PDF invoice. The file is validated and uploaded to the backend.

**Step 2 — Extract text**

Click "Extract Text". The system runs pdfplumber across all pages. If the PDF is scanned or image-based, OCR activates automatically. The extracted text is displayed in the interface.

**Step 3 — Parse the invoice**

Click "Parse Invoice". The extracted text is sent to OpenAI `gpt-4o-mini`. The model returns a JSON object which is validated against the `InvoiceData` schema. A duplicate warning is shown if the invoice matches a previously processed record.

**Step 4 — Review parsed data**

The structured invoice fields are displayed in the dashboard. Review the data for accuracy before proceeding to export.

**Step 5 — Export the result**

Select the desired export format (Excel or CSV) and click "Export". The generated file is saved to the `exports/` directory and a download button is provided in the dashboard.

### Batch Processing

Navigate to the "Batch Processing" tab in the Streamlit dashboard. Upload up to 50 PDF files simultaneously. The system processes each file sequentially with a 1-second delay between requests to manage OpenAI API rate limits. A summary of results is displayed and the consolidated export file is available for download.

---

## Example Output

A successfully parsed invoice returns the following JSON structure:

```json
{
  "invoice_number": "INV-2024-0042",
  "vendor_name": "Global Supplies Ltd",
  "invoice_date": "2024-03-01",
  "due_date": "2024-03-31",
  "tax_amount": 240.0,
  "total_amount": 2640.0,
  "currency": "GBP"
}
```

All fields are optional in the schema. If the AI model cannot confidently extract a value, the field is returned as `null` rather than guessing.

---

## Export System

### Excel

Exported Excel files use `openpyxl` for formatting. Column headers are rendered in bold. Each column width is auto-adjusted to fit the longest value in that column. The human-readable column labels used in the output are:

| Internal Field   | Exported Label |
| ---------------- | -------------- |
| `invoice_number` | Invoice #      |
| `vendor_name`    | Vendor         |
| `invoice_date`   | Invoice Date   |
| `due_date`       | Due Date       |
| `tax_amount`     | Tax Amount     |
| `total_amount`   | Total Amount   |
| `currency`       | Currency       |

### CSV

CSV export follows the same column mapping without any additional formatting. Files are UTF-8 encoded.

### Batch Export

Batch exports consolidate all successfully parsed invoices into a single file. Each invoice occupies one row. Files that cannot be extracted or parsed are silently skipped, and the batch operation continues to completion.

### File Naming

All export filenames follow the pattern `{base_name}_{YYYYMMDD_HHMMSS}.{ext}` to ensure uniqueness and traceability.

---

## Error Handling and Reliability

### File Validation

Every uploaded file is validated for:

- MIME type and file extension (`.pdf` only)
- Non-empty content
- File size not exceeding 10 MB (`MAX_FILE_SIZE_BYTES = 10,485,760`)
- Filename matching the pattern `^[A-Za-z0-9._-]+$`

Invalid files are rejected with an HTTP `400` or `413` response before any processing occurs.

### Path Traversal Protection

File paths are resolved using Python's `Path.resolve()` and verified to be within the configured `uploads/` directory before reading, preventing directory traversal attacks.

### OpenAI Retries

The AI parsing service retries failed OpenAI API calls up to 2 times (`OPENAI_MAX_RETRIES = 2`) with exponential backoff. The delay between retry attempts is `2^attempt` seconds. Each request is subject to a 30-second timeout (`OPENAI_TIMEOUT_SECONDS = 30`).

### API Error Responses

All API errors return structured JSON with an `error` field and an appropriate HTTP status code. This allows the Streamlit frontend and any third-party clients to handle errors programmatically.

---

## Real-World Enhancements

### OCR for Scanned PDFs

Many real-world invoices are scanned images embedded in PDFs. pdfplumber alone cannot extract text from these files. The system detects this condition automatically and activates Tesseract OCR via pdf2image, converting each page to an image before applying character recognition. This makes the pipeline usable on the full range of PDF types encountered in practice.

### Currency Normalisation

Invoice PDFs from different vendors and regions use a variety of currency representations. The `currency_normalizer` service maps common symbols and abbreviations to ISO 4217 codes during the parsing step, producing consistent output regardless of the source document format.

### Duplicate Detection

Reprocessing the same invoice — whether by accident or when resubmitting after a correction — is a common source of data integrity issues. The duplicate detector maintains a rolling log of the 1,000 most recently processed invoices in `data/processed_invoices.json`. A composite key of `(invoice_number, vendor_name, total_amount)` is checked on every parse operation. Detected duplicates are flagged in the API response without blocking the export.

---

## Production Considerations

### AI is Not Re-Run at Export Time

The export endpoint re-runs text extraction and AI parsing to obtain the current data for a given file rather than serving cached results. For high-throughput production use, a persistence layer (e.g., PostgreSQL or Redis) should cache parsed results and serve them directly at export time to avoid repeated API calls and latency.

### Tesseract Path

The OCR service references a hardcoded Tesseract binary path (`C:\Program Files\Tesseract-OCR\tesseract.exe`). On Linux or macOS deployment targets, this path must be updated in `app/services/ocr_extractor.py` or replaced with a `PATH`-based resolution.

### Concurrency

The current implementation uses a single Uvicorn worker. For production deployments handling concurrent requests, run multiple workers with `uvicorn app.main:app --workers 4` or deploy behind Gunicorn with Uvicorn workers.

### Known Limitations

- Batch processing is synchronous and sequential; large batches may take significant time to complete.
- OCR quality is dependent on scan resolution and the Tesseract model version installed.
- Duplicate detection state is file-based and not suitable for multi-instance deployments without a shared storage backend.

---

## Deployment Options

### Streamlit Community Cloud

The Streamlit dashboard can be deployed to [Streamlit Community Cloud](https://streamlit.io/cloud) directly from a public GitHub repository. The FastAPI backend must be hosted separately and the dashboard's base URL updated accordingly.

### Render / Railway

Both [Render](https://render.com) and [Railway](https://railway.app) support Python web services. Deploy the FastAPI backend as a web service using the start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set the `OPENAI_API_KEY` environment variable in the platform's dashboard. Deploy the Streamlit application as a second service on the same platform.

### Docker

The application is structured to support containerisation. A `Dockerfile` would install Python 3.12, Tesseract-OCR, the project dependencies via `uv`, and define separate entry points for the FastAPI and Streamlit processes. Docker Compose can manage both services with a shared volume for the `uploads/`, `exports/`, and `data/` directories.

---

## Monetization Potential

This system is structured as a SaaS-ready prototype. The following commercial models are viable:

**Per-invoice SaaS:** Charge per invoice processed above a free tier (e.g., 50 invoices per month free, then a per-invoice fee). The duplicate detection and history tracking infrastructure supports per-user account scoping with minimal extension.

**Subscription model:** Offer tiered monthly plans based on invoice volume and export format access (e.g., CSV on free tier, Excel and batch export on paid tiers).

**Freelancer delivery:** Package the system as a fully configured, hosted solution delivered to a client's cloud account for a one-time fee, with an optional support retainer.

**White-label integration:** Expose the FastAPI backend as a private API and sell access to accounting software vendors or ERP integrators.

---

## Security Notes

### API Key Management

The OpenAI API key is loaded exclusively from the `.env` file via `python-dotenv`. The key is never logged, returned in API responses, or included in exported files. The `.env` file must be added to `.gitignore` before committing the repository.

### File Validation

All uploaded files are validated for extension, size, and filename character set before being written to disk. UUID-prefixed storage prevents filename collisions and limits the surface area for filename-based attacks.

### Path Traversal

The `safe_upload_path()` utility in `app/utils/file_utils.py` resolves all file paths to their canonical form and verifies they remain within the configured upload directory before any read operation is performed.

### Rate Limiting

The current implementation does not include request-level rate limiting at the API layer. For public-facing deployments, a reverse proxy (nginx, Caddy) or a middleware layer should be configured to limit request frequency per IP address.

---

## Learning Outcomes

This project demonstrates the following real-world engineering skills:

- **AI integration:** Constructing effective prompts for structured data extraction, handling model responses, and implementing retry logic for production reliability.
- **FastAPI backend development:** Designing a multi-endpoint REST API with Pydantic validation, file upload handling, path parameter routing, and structured error responses.
- **Streamlit UI development:** Building a multi-tab, stateful browser application that integrates with a backend API and provides file download functionality.
- **Document processing pipeline:** Combining pdfplumber, PyMuPDF, pdf2image, and Tesseract into a robust extraction pipeline that handles both digital and scanned PDFs.
- **Data export engineering:** Using pandas and openpyxl to generate formatted Excel and CSV exports from structured data.
- **Production patterns:** File sanitisation, duplicate detection, currency normalisation, exponential backoff retry logic, and separation of concerns across API, service, and utility layers.

---

## License

This project is provided for educational and demonstration purposes. No open-source license has been formally applied. All rights reserved unless otherwise specified by the repository owner.
