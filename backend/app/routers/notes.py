from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[schemas.NoteOut])
def list_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_notes(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.NoteOut, status_code=201)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_note(db, note, user_id=current_user.id)


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_note = crud.get_note(db, note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.patch("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_note = crud.update_note(db, note_id, note, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not crud.delete_note(db, note_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Note not found")
