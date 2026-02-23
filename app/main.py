from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import create_db_and_tables, get_session
from app.models import Photo
from app.storage import save_upload, delete_file
from app.models import User
from app.auth import hash_password, verify_password, create_session, delete_session, get_current_user, COOKIE_NAME, get_optional_current_user

app = FastAPI(title="Photo Album")

# --- VÉGLEGES ÚTVONALAK (AZURE PERSISTENCE) ---
BASE_DIR = Path(__file__).resolve().parent

# Ha Azure-on futunk, a védett /home/data mappát használjuk a képeknek
if os.getenv("WEBSITE_SITE_NAME"):
    PERSISTENT_DIR = Path("/home/data")
else:
    # Lokális futtatás esetén a projekt gyökerében lévő 'data' mappát
    PERSISTENT_DIR = BASE_DIR.parent / "data"

STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"
MEDIA_DIR = PERSISTENT_DIR / "media"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()


# --- Segéd: dátum formázás (év-hó-nap óra:perc) ---
def fmt_dt(dt: datetime) -> str:
    # dt timezone aware (UTC). Itt egyszerűen jelenítjük meg:
    return dt.strftime("%Y-%m-%d %H:%M")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/photos", status_code=302)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
def logout_page():
    # a fastapi-users logout route-ja POST, ezért egyszerű redirectet adunk:
    # a template-ből majd POST-olunk /auth/logout-ra
    return RedirectResponse(url="/photos", status_code=302)


@app.get("/photos", response_class=HTMLResponse)
def list_photos(
    request: Request,
    order: str = "date",
    session: Session = Depends(get_session),
):
    stmt = select(Photo)

    if order == "name":
        stmt = stmt.order_by(Photo.name.asc())
    else:
        # dátum szerint (új elöl)
        stmt = stmt.order_by(Photo.uploaded_at.desc())

    photos = session.exec(stmt).all()

    # formázott dátum
    items = [
        {
            "id": p.id,
            "name": p.name,
            "uploaded_at": fmt_dt(p.uploaded_at),
        }
        for p in photos
    ]

    return templates.TemplateResponse(
        "photos.html",
        {"request": request, "photos": items, "order": order},
    )


@app.get("/photos/{photo_id}", response_class=HTMLResponse)
def photo_detail(
    request: Request,
    photo_id: int,
    user: Optional[User] = Depends(get_optional_current_user),
    session: Session = Depends(get_session),
):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Nincs ilyen fotó.")

    # file_path -> /media/filename
    filename = Path(photo.file_path).name
    image_url = f"/media/{filename}"

    return templates.TemplateResponse(
        "photo_detail.html",
        {
            "request": request,
            "photo": {
                "id": photo.id,
                "name": photo.name,
                "uploaded_at": fmt_dt(photo.uploaded_at),
                "image_url": image_url,
                "owner_id": photo.owner_id,
            },
            "user": user,
        },
    )


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_photo(
    request: Request,
    name: str = Form(...),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="A név kötelező.")
    if len(name) > 40:
        raise HTTPException(status_code=400, detail="A név maximum 40 karakter lehet.")

    file_path = await save_upload(image)

    photo = Photo(
        name=name,
        file_path=file_path,
        owner_id=user.id,
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)

    return RedirectResponse(url="/photos", status_code=303)


@app.post("/photos/{photo_id}/delete")
def delete_photo(
    photo_id: int,
    user=Depends(get_current_user),  # csak belépve
    session: Session = Depends(get_session),
):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Nincs ilyen fotó.")

    if photo.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Csak a saját fotódat törölheted.")

    delete_file(photo.file_path)
    session.delete(photo)
    session.commit()

    return RedirectResponse(url="/photos", status_code=303)
@app.post("/auth/register")
def auth_register(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    email = email.strip().lower()
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email és jelszó kötelező.")

    exists = session.exec(select(User).where(User.email == email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Már létezik ilyen email.")

    user = User(email=email, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    return RedirectResponse(url="/login", status_code=303)


@app.post("/auth/login")
def auth_login(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    email = email.strip().lower()
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Hibás email vagy jelszó.")

    sid = create_session(session, user)
    resp = RedirectResponse(url="/photos", status_code=303)
    resp.set_cookie(COOKIE_NAME, sid, httponly=True, samesite="lax")
    return resp

@app.post("/auth/logout")
def auth_logout(
    request: Request,
    session: Session = Depends(get_session),
):
    sid = request.cookies.get(COOKIE_NAME)
    if sid:
        delete_session(session, sid)
    response = RedirectResponse(url="/photos", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response
