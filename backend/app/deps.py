# backend/app/deps.py
import os
from sqlmodel import create_engine, Session
from app.config import Settings

settings = Settings()

DB_PATH = os.path.abspath("data/db.sqlite")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as s:
        yield s
