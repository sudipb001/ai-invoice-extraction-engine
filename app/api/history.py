from fastapi import APIRouter, HTTPException

from app.config import UPLOAD_DIR, EXPORT_DIR

router = APIRouter()


@router.get("/history")
def history():
    try:
        uploads = [f.name for f in UPLOAD_DIR.glob("*")]
        exports = [f.name for f in EXPORT_DIR.glob("*")]

        return {
            "success": True,
            "uploaded_files": uploads,
            "exported_files": exports
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load history."
        )
