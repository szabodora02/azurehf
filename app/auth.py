from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Depends, Request, Response, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import User, SessionToken

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
pwd_context = PasswordHash((BcryptHasher(),))

COOKIE_NAME = "photoalbum_session"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_session(db: Session, user: User) -> str:
    token = SessionToken(user_id=user.id)
    db.add(token)
    db.commit()
    db.refresh(token)
    return str(token.id)


def delete_session(db: Session, session_id: str) -> None:
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        return
    token = db.get(SessionToken, sid)
    if token:
        db.delete(token)
        db.commit()


def get_current_user(
    request: Request,
    db: Session = Depends(get_session),
) -> User:
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = db.get(SessionToken, sid)
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.get(User, token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user
def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_session),
) -> Optional[User]:
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        return None
    token = db.get(SessionToken, sid)
    if not token:
        return None
    return db.get(User, token.user_id)
