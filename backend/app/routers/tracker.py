from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/tracker", tags=["tracker"])


@router.get("/", response_model=list[schemas.TrackerRowOut])
def list_rows(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    return crud.get_tracker_rows(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.TrackerRowOut, status_code=201)
def create_row(row: schemas.TrackerRowCreate, db: Session = Depends(get_db)):
    return crud.create_tracker_row(db, row)


@router.get("/{row_id}", response_model=schemas.TrackerRowOut)
def get_row(row_id: int, db: Session = Depends(get_db)):
    db_row = crud.get_tracker_row(db, row_id)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Tracker row not found")
    return db_row


@router.patch("/{row_id}", response_model=schemas.TrackerRowOut)
def update_row(row_id: int, row: schemas.TrackerRowUpdate, db: Session = Depends(get_db)):
    db_row = crud.update_tracker_row(db, row_id, row)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Tracker row not found")
    return db_row


@router.delete("/{row_id}", status_code=204)
def delete_row(row_id: int, db: Session = Depends(get_db)):
    if not crud.delete_tracker_row(db, row_id):
        raise HTTPException(status_code=404, detail="Tracker row not found")
