from pathlib import Path

BASE_DIR = Path(".")
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"

UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

OPENAI_TIMEOUT_SECONDS = 30
OPENAI_MAX_RETRIES = 2

MAX_BATCH_SIZE = 50
BATCH_INTER_FILE_DELAY = 1  # seconds between AI calls

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

PROCESSED_INVOICES_FILE = DATA_DIR / "processed_invoices.json"
