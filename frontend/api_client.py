import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 10


def _url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def _auth_headers() -> dict:
    token = st.session_state.get("auth_token")
    if not token:
        raise RuntimeError("Not logged in.")
    return {"Authorization": f"Bearer {token}"}


def check_health() -> bool:
    try:
        resp = requests.get(_url("/health"), timeout=TIMEOUT)
        return resp.ok
    except requests.RequestException:
        return False


# ---------- Auth ----------

def register(username: str, password: str) -> dict:
    resp = requests.post(
        _url("/auth/register"), json={"username": username, "password": password}, timeout=TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()


def login(username: str, password: str) -> str:
    resp = requests.post(
        _url("/auth/login"), json={"username": username, "password": password}, timeout=TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_me() -> dict:
    resp = requests.get(_url("/auth/me"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def forgot_password(username: str) -> dict:
    resp = requests.post(_url("/auth/forgot-password"), json={"username": username}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def reset_password(token: str, new_password: str) -> dict:
    resp = requests.post(
        _url("/auth/reset-password"),
        json={"token": token, "new_password": new_password},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ---------- Todos ----------

def get_todos() -> list[dict]:
    resp = requests.get(_url("/todos/"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_todo(title: str, description: str | None, priority: str) -> dict:
    resp = requests.post(
        _url("/todos/"),
        json={"title": title, "description": description, "priority": priority},
        headers=_auth_headers(),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def update_todo(todo_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/todos/{todo_id}"), json=fields, headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_todo(todo_id: int) -> None:
    resp = requests.delete(_url(f"/todos/{todo_id}"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Notes ----------

def get_notes() -> list[dict]:
    resp = requests.get(_url("/notes/"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_note(title: str, content: str) -> dict:
    resp = requests.post(
        _url("/notes/"), json={"title": title, "content": content}, headers=_auth_headers(), timeout=TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()


def update_note(note_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/notes/{note_id}"), json=fields, headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_note(note_id: int) -> None:
    resp = requests.delete(_url(f"/notes/{note_id}"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Tracker ----------

def get_tracker_rows() -> list[dict]:
    resp = requests.get(_url("/tracker/"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_tracker_row(**fields) -> dict:
    resp = requests.post(_url("/tracker/"), json=fields, headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def update_tracker_row(row_id: int, **fields) -> dict:
    resp = requests.patch(_url(f"/tracker/{row_id}"), json=fields, headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def delete_tracker_row(row_id: int) -> None:
    resp = requests.delete(_url(f"/tracker/{row_id}"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Documents ----------

def get_documents() -> list[dict]:
    resp = requests.get(_url("/documents/"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def upload_document(filename: str, file_bytes: bytes, content_type: str) -> dict:
    resp = requests.post(
        _url("/documents/upload"),
        files={"file": (filename, file_bytes, content_type)},
        headers=_auth_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def delete_document(doc_id: int) -> None:
    resp = requests.delete(_url(f"/documents/{doc_id}"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()


# ---------- Chat ----------

def get_models() -> list[str]:
    resp = requests.get(_url("/chat/models"), headers=_auth_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def chat(message: str, model: str | None = None, history: list[dict] | None = None) -> dict:
    resp = requests.post(
        _url("/chat/"),
        json={"message": message, "model": model, "history": history or []},
        headers=_auth_headers(),
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def chat_stream(message: str, model: str | None = None, history: list[dict] | None = None):
    with requests.post(
        _url("/chat/stream"),
        json={"message": message, "model": model, "history": history or []},
        headers=_auth_headers(),
        timeout=120,
        stream=True,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                yield line
