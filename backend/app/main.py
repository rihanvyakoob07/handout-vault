# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.deps import engine
from app.routers import auth, handouts
from app.config import Settings

settings = Settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def init():
    SQLModel.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(handouts.router)

@app.get("/")
def root():
    return {"status": "ok"}
