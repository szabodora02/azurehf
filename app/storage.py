import os
import secrets
from pathlib import Path
from fastapi import UploadFile, HTTPException

if os.getenv("WEBSITE_SITE_NAME"):
    PERSISTENT_DIR = Path("/home/data")
else:
    PERSISTENT_DIR = Path(__file__).resolve().parent.parent / "data"

MEDIA_DIR = PERSISTENT_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

# ... a függvények maradnak ...
# ... (a fájl többi része változatlan marad)

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
