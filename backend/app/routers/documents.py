import os
import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import config, crud, schemas
from ..database import get_db
from ..rag.ingest import SUPPORTED_EXTENSIONS, delete_document_vectors, ingest_file

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=list[schemas.DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return crud.get_documents(db)


@router.post("/upload", response_model=schemas.DocumentOut, status_code=201)
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
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

    db_doc = crud.create_document(db, filename=file.filename, num_chunks=0)

    try:
        num_chunks = ingest_file(temp_path, doc_id=db_doc.id, filename=file.filename)
    except Exception as exc:
        crud.delete_document(db, db_doc.id)
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {exc}") from exc
    finally:
        os.remove(temp_path)

    db_doc.num_chunks = num_chunks
    db.commit()
    db.refresh(db_doc)
    return db_doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    if not crud.get_document(db, doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document_vectors(doc_id)
    crud.delete_document(db, doc_id)
