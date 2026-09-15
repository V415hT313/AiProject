import json

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import auth, config, crud, models, schemas
from ..database import SessionLocal, get_db
from ..rag.chain import build_rag_chain, to_lc_messages

router = APIRouter(prefix="/chat", tags=["chat"])

OLLAMA_UNREACHABLE_MESSAGE = (
    "Could not reach the Ollama server. Make sure Ollama is running and reachable "
    f"at {config.OLLAMA_BASE_URL}."
)

TITLE_MAX_LENGTH = 50


def _make_title(message: str) -> str:
    message = message.strip()
    if len(message) <= TITLE_MAX_LENGTH:
        return message
    return message[:TITLE_MAX_LENGTH].rstrip() + "..."


NEW_CHAT_TITLE = "New chat"


def _get_or_create_session(
    db: Session, user_id: int, session_id: int | None, first_message: str
) -> models.ChatSession:
    if session_id is not None:
        session = crud.get_chat_session(db, session_id, user_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
        # A session created just to attach a document (before any text message)
        # still has the placeholder title — retitle it once a real message arrives.
        if session.title == NEW_CHAT_TITLE and not crud.get_chat_messages(db, session.id):
            session.title = _make_title(first_message)
            db.commit()
        return session
    return crud.create_chat_session(db, user_id, title=_make_title(first_message))


@router.get("/models", response_model=list[str])
def list_models(current_user: models.User = Depends(auth.get_current_user)):
    try:
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail=OLLAMA_UNREACHABLE_MESSAGE) from exc

    ollama_models = resp.json().get("models", [])
    return [m["name"] for m in ollama_models if "completion" in m.get("capabilities", [])]


@router.get("/sessions", response_model=list[schemas.ChatSessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_chat_sessions(db, user_id=current_user.id)


@router.post("/sessions", response_model=schemas.ChatSessionOut, status_code=201)
def create_session(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_chat_session(db, user_id=current_user.id, title=NEW_CHAT_TITLE)


@router.get("/sessions/{session_id}/messages", response_model=list[schemas.ChatMessageOut])
def get_session_messages(
    session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    session = crud.get_chat_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = crud.get_chat_messages(db, session_id)
    return [
        schemas.ChatMessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=json.loads(m.sources) if m.sources else [],
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)
):
    if not crud.delete_chat_session(db, session_id, current_user.id):
        raise HTTPException(status_code=404, detail="Chat session not found")


def _sources_from_docs(docs) -> list[str]:
    seen = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        if source not in seen:
            seen.append(source)
    return seen


@router.post("/", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = _get_or_create_session(db, current_user.id, request.session_id, request.message)
    crud.add_chat_message(db, session.id, "user", request.message)

    try:
        chain, retriever = build_rag_chain(user_id=current_user.id, session_id=session.id, model=request.model)
        docs = retriever.invoke(request.message)
        history = to_lc_messages([m.model_dump() for m in request.history])
        answer = chain.invoke({"question": request.message, "history": history})
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"{OLLAMA_UNREACHABLE_MESSAGE} ({exc})") from exc

    sources = _sources_from_docs(docs)
    crud.add_chat_message(db, session.id, "assistant", answer, sources)

    return schemas.ChatResponse(answer=answer, sources=sources, session_id=session.id)


@router.post("/stream")
def chat_stream(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    user_id = current_user.id
    session = _get_or_create_session(db, user_id, request.session_id, request.message)
    session_id = session.id
    crud.add_chat_message(db, session_id, "user", request.message)
    history = to_lc_messages([m.model_dump() for m in request.history])

    def event_generator():
        # Depends(get_db) closes its session before a StreamingResponse body
        # actually starts iterating, so any DB work here needs its own session.
        yield json.dumps({"type": "session", "session_id": session_id}) + "\n"
        full_response = ""
        try:
            chain, retriever = build_rag_chain(
                user_id=user_id, session_id=session_id, model=request.model, streaming=True
            )
            docs = retriever.invoke(request.message)
            sources = _sources_from_docs(docs)
            yield json.dumps({"type": "sources", "sources": sources}) + "\n"
            for token in chain.stream({"question": request.message, "history": history}):
                full_response += token
                yield json.dumps({"type": "token", "content": token}) + "\n"

            stream_db = SessionLocal()
            try:
                crud.add_chat_message(stream_db, session_id, "assistant", full_response, sources)
            finally:
                stream_db.close()

            yield json.dumps({"type": "done"}) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": f"{OLLAMA_UNREACHABLE_MESSAGE} ({exc})"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
