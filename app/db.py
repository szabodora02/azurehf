import os
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# 1. Kiszámoljuk az útvonalat
BASE_DIR = Path(__file__).resolve().parent

# 2. Beállítjuk a data_dir-t
data_dir_str = os.getenv("APP_DATA_DIR", str(BASE_DIR))
data_dir = Path(data_dir_str)

# 3. ITT A LÉNYEG: Létrehozzuk a mappát, ha nem létezik!
data_dir.mkdir(parents=True, exist_ok=True)

# 4. Összerakjuk az URL-t
default_sqlite_path = data_dir / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_sqlite_path}")

# SQLite-nál kell ez a connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
