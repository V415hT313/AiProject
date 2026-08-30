from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import notes, todos, tracker

models.Base.metadata.create_all(bind=engine)

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


@app.get("/health")
def health():
    return {"status": "ok"}
