# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FIREBASE_CREDENTIALS: str = "firebase.json"
    STORAGE_PATH: str = "./data/storage"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
