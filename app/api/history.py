from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
EXPORT_DIR = Path("exports")

@router.get("/history")
def history():
    uploads = [f.name for f in UPLOAD_DIR.glob("*")]
    exports = [f.name for f in EXPORT_DIR.glob("*")]

    return {
        "success": True,
        "uploaded_files": uploads,
        "exported_files": exports
    }
