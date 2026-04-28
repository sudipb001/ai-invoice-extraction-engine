from pathlib import Path
from fastapi import HTTPException
import re

SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def sanitize_filename(name: str) -> str:
    if not name:
        raise HTTPException(status_code=400, detail="Filename missing.")

    clean = Path(name).name

    if not SAFE_NAME_PATTERN.match(clean):
        raise HTTPException(
            status_code=400,
            detail="Filename contains invalid characters."
        )

    return clean


def safe_upload_path(upload_dir: Path, filename: str) -> Path:
    clean = sanitize_filename(filename)
    path = upload_dir / clean
    resolved = path.resolve()
    upload_root = upload_dir.resolve()

    if upload_root not in resolved.parents and resolved != upload_root:
        raise HTTPException(
            status_code=400,
            detail="Invalid file path."
        )

    return path
