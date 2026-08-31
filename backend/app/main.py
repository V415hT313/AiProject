import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, models
from .database import engine
from .routers import chat, documents, notes, todos, tracker

models.Base.metadata.create_all(bind=engine)
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.CHROMA_DIR, exist_ok=True)

app = FastAPI(title="AiProject API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)
app.include_router(notes.router)
app.include_router(tracker.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
