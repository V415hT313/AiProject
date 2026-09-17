from api_client import get_document_count as _get_document_count
from api_client import get_notes, get_todos


def get_open_todo_count() -> int:
    todos = get_todos()
    return sum(1 for todo in todos if not todo["done"])


def get_recent_notes(limit: int = 5) -> list[dict]:
    notes = get_notes()
    notes_sorted = sorted(notes, key=lambda n: n["created_at"], reverse=True)
    return notes_sorted[:limit]


def get_document_count() -> int:
    return _get_document_count()
