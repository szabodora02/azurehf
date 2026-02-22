import os
import secrets
from pathlib import Path

from fastapi import UploadFile, HTTPException

MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "./media"))
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def _safe_ext(filename: str) -> str:
    ext = Path(filename.lower()).suffix
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Csak jpg/jpeg/png/webp engedélyezett.")
    return ext


async def save_upload(file: UploadFile) -> str:
    ext = _safe_ext(file.filename or "")
    token = secrets.token_hex(16)
    filename = f"{token}{ext}"
    dest = MEDIA_DIR / filename

    # streaming mentés
    with dest.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    return str(dest)


def delete_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
