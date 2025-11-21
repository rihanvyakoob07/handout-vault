from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Handout Vault (Local)"
    ENV: str = "development"

    # Auth
    SECRET_KEY: str = Field("change-me-in-prod", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Storage (local)
    STORAGE_PATH: str = Field("./data/storage", env="STORAGE_PATH")
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 MB

    # CORS
    ALLOW_ORIGINS: List[str] = Field(["http://localhost:3000"], env="ALLOW_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
