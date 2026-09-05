import json

import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import config, schemas
from ..rag.chain import build_rag_chain

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/models", response_model=list[str])
def list_models():
    resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    models = resp.json().get("models", [])
    return [m["name"] for m in models if "completion" in m.get("capabilities", [])]


def _sources_from_docs(docs) -> list[str]:
    seen = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        if source not in seen:
            seen.append(source)
    return seen


@router.post("/", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest):
    chain, retriever = build_rag_chain(model=request.model)
    docs = retriever.invoke(request.message)
    answer = chain.invoke(request.message)
    return schemas.ChatResponse(answer=answer, sources=_sources_from_docs(docs))


@router.post("/stream")
def chat_stream(request: schemas.ChatRequest):
    chain, retriever = build_rag_chain(model=request.model, streaming=True)

    def event_generator():
        docs = retriever.invoke(request.message)
        yield json.dumps({"type": "sources", "sources": _sources_from_docs(docs)}) + "\n"
        for token in chain.stream(request.message):
            yield json.dumps({"type": "token", "content": token}) + "\n"
        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
