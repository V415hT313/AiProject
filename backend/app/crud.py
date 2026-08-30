from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas

# ---------- Todo ----------

def get_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    return db.get(models.Todo, todo_id)


def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).order_by(models.Todo.id.desc()).offset(skip).limit(limit).all()


def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate) -> Optional[models.Todo]:
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        return None
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        return False
    db.delete(db_todo)
    db.commit()
    return True


# ---------- Note ----------

def get_note(db: Session, note_id: int) -> Optional[models.Note]:
    return db.get(models.Note, note_id)


def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Note).order_by(models.Note.id.desc()).offset(skip).limit(limit).all()


def create_note(db: Session, note: schemas.NoteCreate) -> models.Note:
    db_note = models.Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: schemas.NoteUpdate) -> Optional[models.Note]:
    db_note = get_note(db, note_id)
    if db_note is None:
        return None
    for key, value in note.model_dump(exclude_unset=True).items():
        setattr(db_note, key, value)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int) -> bool:
    db_note = get_note(db, note_id)
    if db_note is None:
        return False
    db.delete(db_note)
    db.commit()
    return True


# ---------- TrackerRow ----------

def get_tracker_row(db: Session, row_id: int) -> Optional[models.TrackerRow]:
    return db.get(models.TrackerRow, row_id)


def get_tracker_rows(db: Session, skip: int = 0, limit: int = 500):
    return db.query(models.TrackerRow).order_by(models.TrackerRow.id.desc()).offset(skip).limit(limit).all()


def create_tracker_row(db: Session, row: schemas.TrackerRowCreate) -> models.TrackerRow:
    db_row = models.TrackerRow(**row.model_dump())
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


def update_tracker_row(db: Session, row_id: int, row: schemas.TrackerRowUpdate) -> Optional[models.TrackerRow]:
    db_row = get_tracker_row(db, row_id)
    if db_row is None:
        return None
    for key, value in row.model_dump(exclude_unset=True).items():
        setattr(db_row, key, value)
    db.commit()
    db.refresh(db_row)
    return db_row


def delete_tracker_row(db: Session, row_id: int) -> bool:
    db_row = get_tracker_row(db, row_id)
    if db_row is None:
        return False
    db.delete(db_row)
    db.commit()
    return True
