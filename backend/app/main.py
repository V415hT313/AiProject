import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config, models
from .database import engine
from .routers import auth, chat, documents, notes, todos, tracker

logger = logging.getLogger("aiproject")

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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(notes.router)
app.include_router(tracker.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
