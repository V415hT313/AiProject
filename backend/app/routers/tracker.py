from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/tracker", tags=["tracker"])


@router.get("/", response_model=list[schemas.TrackerRowOut])
def list_rows(
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_tracker_rows(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.TrackerRowOut, status_code=201)
def create_row(
    row: schemas.TrackerRowCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_tracker_row(db, row, user_id=current_user.id)


@router.get("/{row_id}", response_model=schemas.TrackerRowOut)
def get_row(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_row = crud.get_tracker_row(db, row_id, user_id=current_user.id)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Tracker row not found")
    return db_row


@router.patch("/{row_id}", response_model=schemas.TrackerRowOut)
def update_row(
    row_id: int,
    row: schemas.TrackerRowUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_row = crud.update_tracker_row(db, row_id, row, user_id=current_user.id)
    if db_row is None:
        raise HTTPException(status_code=404, detail="Tracker row not found")
    return db_row


@router.delete("/{row_id}", status_code=204)
def delete_row(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not crud.delete_tracker_row(db, row_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Tracker row not found")
