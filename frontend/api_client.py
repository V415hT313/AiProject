import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 10


def _url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def check_health() -> bool:
    try:
        resp = requests.get(_url("/health"), timeout=TIMEOUT)
        return resp.ok
    except requests.RequestException:
        return False


# ---------- Todos ----------

def get_todos() -> list[dict]:
    resp = requests.get(_url("/todos/"), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_todo(title: str, description: str | None, priority: str) -> dict:
    resp = requests.post(
        _url("/todos/"),
        json={"title": title, "description": description, "priority": priority},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def update_todo(todo_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/todos/{todo_id}"), json=fields, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_todo(todo_id: int) -> None:
    resp = requests.delete(_url(f"/todos/{todo_id}"), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Notes ----------

def get_notes() -> list[dict]:
    resp = requests.get(_url("/notes/"), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_note(title: str, content: str) -> dict:
    resp = requests.post(_url("/notes/"), json={"title": title, "content": content}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def update_note(note_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/notes/{note_id}"), json=fields, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_note(note_id: int) -> None:
    resp = requests.delete(_url(f"/notes/{note_id}"), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Tracker ----------

def get_tracker_rows() -> list[dict]:
    resp = requests.get(_url("/tracker/"), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_tracker_row(**fields) -> dict:
    resp = requests.post(_url("/tracker/"), json=fields, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def update_tracker_row(row_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/tracker/{row_id}"), json=fields, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_tracker_row(row_id: int) -> None:
    resp = requests.delete(_url(f"/tracker/{row_id}"), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Documents ----------

def get_documents() -> list[dict]:
    resp = requests.get(_url("/documents/"), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def upload_document(filename: str, file_bytes: bytes, content_type: str) -> dict:
    resp = requests.post(
        _url("/documents/upload"),
        files={"file": (filename, file_bytes, content_type)},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def delete_document(doc_id: int) -> None:
    resp = requests.delete(_url(f"/documents/{doc_id}"), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Chat ----------

def chat(message: str, model: str | None = None) -> dict:
    resp = requests.post(_url("/chat/"), json={"message": message, "model": model}, timeout=120)
    resp.raise_for_status()
    return resp.json()


def chat_stream(message: str, model: str | None = None):
    with requests.post(
        _url("/chat/stream"),
        json={"message": message, "model": model},
        timeout=120,
        stream=True,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                yield line
