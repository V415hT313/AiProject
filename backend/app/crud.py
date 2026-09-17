import datetime
import json
from typing import Optional

from sqlalchemy.orm import Session

from . import auth, config, models, schemas

# ---------- User ----------

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(username=user.username, hashed_password=auth.hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: models.User, new_password: str) -> None:
    user.hashed_password = auth.hash_password(new_password)
    db.commit()


# ---------- PasswordResetToken ----------

def create_password_reset_token(db: Session, user_id: int) -> models.PasswordResetToken:
    token = models.PasswordResetToken(
        user_id=user_id,
        token=auth.generate_reset_token(),
        expires_at=datetime.datetime.utcnow()
        + datetime.timedelta(minutes=config.RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_valid_reset_token(db: Session, token: str) -> Optional[models.PasswordResetToken]:
    return (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.token == token,
            models.PasswordResetToken.used.is_(False),
            models.PasswordResetToken.expires_at > datetime.datetime.utcnow(),
        )
        .first()
    )


def mark_reset_token_used(db: Session, reset_token: models.PasswordResetToken) -> None:
    reset_token.used = True
    db.commit()


# ---------- Todo ----------

def get_todo(db: Session, todo_id: int, user_id: int) -> Optional[models.Todo]:
    return db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.user_id == user_id).first()


def get_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Todo)
        .filter(models.Todo.user_id == user_id)
        .order_by(models.Todo.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_todo(db: Session, todo: schemas.TodoCreate, user_id: int) -> models.Todo:
    db_todo = models.Todo(**todo.model_dump(), user_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate, user_id: int) -> Optional[models.Todo]:
    db_todo = get_todo(db, todo_id, user_id)
    if db_todo is None:
        return None
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int, user_id: int) -> bool:
    db_todo = get_todo(db, todo_id, user_id)
    if db_todo is None:
        return False
    db.delete(db_todo)
    db.commit()
    return True


# ---------- Note ----------

def get_note(db: Session, note_id: int, user_id: int) -> Optional[models.Note]:
    return db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()


def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Note)
        .filter(models.Note.user_id == user_id)
        .order_by(models.Note.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_note(db: Session, note: schemas.NoteCreate, user_id: int) -> models.Note:
    db_note = models.Note(**note.model_dump(), user_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: schemas.NoteUpdate, user_id: int) -> Optional[models.Note]:
    db_note = get_note(db, note_id, user_id)
    if db_note is None:
        return None
    for key, value in note.model_dump(exclude_unset=True).items():
        setattr(db_note, key, value)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    db_note = get_note(db, note_id, user_id)
    if db_note is None:
        return False
    db.delete(db_note)
    db.commit()
    return True


# ---------- Document ----------

def get_document(db: Session, doc_id: int, user_id: int) -> Optional[models.Document]:
    return (
        db.query(models.Document)
        .filter(models.Document.id == doc_id, models.Document.user_id == user_id)
        .first()
    )


def get_documents(db: Session, user_id: int, session_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Document)
        .filter(models.Document.user_id == user_id, models.Document.session_id == session_id)
        .order_by(models.Document.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_document_count(db: Session, user_id: int) -> int:
    return db.query(models.Document).filter(models.Document.user_id == user_id).count()


def create_document(
    db: Session, filename: str, num_chunks: int, user_id: int, session_id: int
) -> models.Document:
    db_doc = models.Document(
        filename=filename, num_chunks=num_chunks, user_id=user_id, session_id=session_id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
    db_doc = get_document(db, doc_id, user_id)
    if db_doc is None:
        return False
    db.delete(db_doc)
    db.commit()
    return True


# ---------- ChatSession / ChatMessage ----------

def create_chat_session(db: Session, user_id: int, title: str) -> models.ChatSession:
    session = models.ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_chat_sessions(db: Session, user_id: int) -> list[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user_id)
        .order_by(models.ChatSession.updated_at.desc())
        .all()
    )


def get_chat_session(db: Session, session_id: int, user_id: int) -> Optional[models.ChatSession]:
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.id == session_id, models.ChatSession.user_id == user_id)
        .first()
    )


def delete_chat_session(db: Session, session_id: int, user_id: int) -> bool:
    session = get_chat_session(db, session_id, user_id)
    if session is None:
        return False
    db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return True


def add_chat_message(
    db: Session, session_id: int, role: str, content: str, sources: Optional[list[str]] = None
) -> models.ChatMessage:
    message = models.ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        sources=json.dumps(sources or []),
    )
    db.add(message)

    session = db.get(models.ChatSession, session_id)
    session.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(message)
    return message


def get_chat_messages(db: Session, session_id: int) -> list[models.ChatMessage]:
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.id.asc())
        .all()
    )


# ---------- TrackerRow ----------

def get_tracker_row(db: Session, row_id: int, user_id: int) -> Optional[models.TrackerRow]:
    return (
        db.query(models.TrackerRow)
        .filter(models.TrackerRow.id == row_id, models.TrackerRow.user_id == user_id)
        .first()
    )


def get_tracker_rows(db: Session, user_id: int, skip: int = 0, limit: int = 500):
    return (
        db.query(models.TrackerRow)
        .filter(models.TrackerRow.user_id == user_id)
        .order_by(models.TrackerRow.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_tracker_row(db: Session, row: schemas.TrackerRowCreate, user_id: int) -> models.TrackerRow:
    db_row = models.TrackerRow(**row.model_dump(), user_id=user_id)
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


def update_tracker_row(
    db: Session, row_id: int, row: schemas.TrackerRowUpdate, user_id: int
) -> Optional[models.TrackerRow]:
    db_row = get_tracker_row(db, row_id, user_id)
    if db_row is None:
        return None
    for key, value in row.model_dump(exclude_unset=True).items():
        setattr(db_row, key, value)
    db.commit()
    db.refresh(db_row)
    return db_row


def delete_tracker_row(db: Session, row_id: int, user_id: int) -> bool:
    db_row = get_tracker_row(db, row_id, user_id)
    if db_row is None:
        return False
    db.delete(db_row)
    db.commit()
    return True
