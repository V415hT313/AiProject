from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[schemas.TodoOut])
def list_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_todos(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=schemas.TodoOut, status_code=201)
def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_todo(db, todo, user_id=current_user.id)


@router.get("/{todo_id}", response_model=schemas.TodoOut)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_todo = crud.get_todo(db, todo_id, user_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@router.patch("/{todo_id}", response_model=schemas.TodoOut)
def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_todo = crud.update_todo(db, todo_id, todo, user_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not crud.delete_todo(db, todo_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Todo not found")
