import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

if os.getenv("WEBSITE_SITE_NAME"):
    PERSISTENT_DIR = Path("/home/data")
else:
    PERSISTENT_DIR = Path(__file__).resolve().parent.parent / "data"

PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)
default_sqlite_path = PERSISTENT_DIR / "app.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_sqlite_path}")

connect_args = {
    "check_same_thread": False,
    "timeout": 15
} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args=connect_args,
    pool_recycle=3600,
    pool_pre_ping=True
)

# ... a függvények maradnak ...
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
