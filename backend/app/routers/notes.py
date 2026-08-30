from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[schemas.NoteOut])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notes(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.NoteOut, status_code=201)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, note)


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.patch("/{note_id}", response_model=schemas.NoteOut)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db, note_id, note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    if not crud.delete_note(db, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
