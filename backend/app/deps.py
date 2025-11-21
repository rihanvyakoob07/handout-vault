from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.config import settings
import os

# Use SQLite for local dev. File path: ./data/db.sqlite
db_path = os.environ.get("DATABASE_URL", "sqlite:///./data/db.sqlite")

engine = create_engine(db_path, connect_args={"check_same_thread": False} if db_path.startswith("sqlite") else {})

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
