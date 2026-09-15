import os
import pathlib
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import auth, config, crud, models, schemas
from ..database import get_db
from ..rag.ingest import SUPPORTED_EXTENSIONS, delete_document_vectors, ingest_file

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_owned_session(db: Session, session_id: int, user_id: int) -> models.ChatSession:
    session = crud.get_chat_session(db, session_id, user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.get("/", response_model=list[schemas.DocumentOut])
def list_documents(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_session(db, session_id, current_user.id)
    return crud.get_documents(db, user_id=current_user.id, session_id=session_id)


@router.post("/upload", response_model=schemas.DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile,
    session_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    _get_owned_session(db, session_id, current_user.id)

    ext = pathlib.Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(config.UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    db_doc = crud.create_document(
        db, filename=file.filename, num_chunks=0, user_id=current_user.id, session_id=session_id
    )

    try:
        num_chunks = ingest_file(
            temp_path,
            doc_id=db_doc.id,
            filename=file.filename,
            user_id=current_user.id,
            session_id=session_id,
        )
    except Exception as exc:
        crud.delete_document(db, db_doc.id, user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {exc}") from exc
    finally:
        os.remove(temp_path)

    db_doc.num_chunks = num_chunks
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not crud.get_document(db, doc_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document_vectors(doc_id, user_id=current_user.id)
    crud.delete_document(db, doc_id, user_id=current_user.id)
