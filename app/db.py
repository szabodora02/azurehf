import os
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path
from pathlib import Path

default_sqlite_path = Path(os.getenv("APP_DATA_DIR", "./")).joinpath("app.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_sqlite_path}")
# SQLite-nál kell ez a connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
