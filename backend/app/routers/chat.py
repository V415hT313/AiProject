import json

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .. import auth, config, models, schemas
from ..rag.chain import build_rag_chain

router = APIRouter(prefix="/chat", tags=["chat"])

OLLAMA_UNREACHABLE_MESSAGE = (
    "Could not reach the Ollama server. Make sure Ollama is running and reachable "
    f"at {config.OLLAMA_BASE_URL}."
)


@router.get("/models", response_model=list[str])
def list_models(current_user: models.User = Depends(auth.get_current_user)):
    try:
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail=OLLAMA_UNREACHABLE_MESSAGE) from exc

    ollama_models = resp.json().get("models", [])
    return [m["name"] for m in ollama_models if "completion" in m.get("capabilities", [])]


def _sources_from_docs(docs) -> list[str]:
    seen = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        if source not in seen:
            seen.append(source)
    return seen


@router.post("/", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        chain, retriever = build_rag_chain(user_id=current_user.id, model=request.model)
        docs = retriever.invoke(request.message)
        answer = chain.invoke(request.message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"{OLLAMA_UNREACHABLE_MESSAGE} ({exc})") from exc

    return schemas.ChatResponse(answer=answer, sources=_sources_from_docs(docs))


@router.post("/stream")
def chat_stream(request: schemas.ChatRequest, current_user: models.User = Depends(auth.get_current_user)):
    user_id = current_user.id

    def event_generator():
        try:
            chain, retriever = build_rag_chain(user_id=user_id, model=request.model, streaming=True)
            docs = retriever.invoke(request.message)
            yield json.dumps({"type": "sources", "sources": _sources_from_docs(docs)}) + "\n"
            for token in chain.stream(request.message):
                yield json.dumps({"type": "token", "content": token}) + "\n"
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": f"{OLLAMA_UNREACHABLE_MESSAGE} ({exc})"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
