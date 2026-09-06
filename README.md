# AiProject

A local, self-hosted personal productivity assistant: an AI chatbot with document-grounded
answers (RAG), a to-do list, a notes app with markdown preview, and a habit/expense tracker —
all backed by your own machine, your own data, and a locally-running LLM.

## Features

- **AI Chatbot** — ask questions about documents you upload; answers are grounded in their
  content via Retrieval-Augmented Generation, streamed token-by-token, with source citations.
  Attach a PDF/TXT/MD file directly from the chat box to add it to the knowledge base.
- **To-do List** — checkboxes, color-coded priorities (🔴 high / 🟡 medium / 🟢 low).
- **Notes** — markdown editor with a live side-by-side preview.
- **Tracker** — a spreadsheet-style grid (add/edit/delete rows inline) with Excel export.
- **Home dashboard** — at-a-glance stats: open todos, ingested document count, recent notes.

## Architecture

```
Streamlit frontend  →  FastAPI backend  →  Postgres (data)
  (4 pages)                │            →  ChromaDB + Ollama (RAG / local LLM)
                            └── talks to Ollama running natively on the host
```

- **Frontend**: Streamlit multi-page app, calling the backend over plain HTTP.
- **Backend**: FastAPI + SQLAlchemy, exposing REST endpoints for todos/notes/tracker/documents/chat.
- **Data layer**: Postgres for structured data (todos, notes, tracker rows, document metadata).
- **AI layer**: LangChain + ChromaDB (vector store) + Ollama (local LLM and embedding model).

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| RAG | LangChain, ChromaDB |
| LLM | Ollama (`llama3.2` chat, `nomic-embed-text` embeddings) |
| Containerization | Docker Compose |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/download) installed **natively on your host machine** (not
  containerized — the backend container reaches it via `host.docker.internal`), with the
  required models pulled:
  ```
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```

## Setup & running

1. Clone the repo and copy the environment template:
   ```
   cp .env.example .env
   ```
   Edit `.env` and set your own `POSTGRES_USER` / `POSTGRES_PASSWORD`.

2. Make sure Ollama is running (it starts automatically after install on most systems; verify
   with `ollama list`).

3. Start everything:
   ```
   docker compose up -d --build
   ```

4. Open the app:
   - Streamlit UI: http://localhost:8501
   - FastAPI docs (Swagger UI): http://localhost:8000/docs

To stop everything: `docker compose down` (add `-v` to also wipe the database/vector store volumes).

## Local development (without Docker)

Each service has its own virtual environment and can be run directly for faster iteration:

```
# Backend
cd backend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python -m streamlit run Home.py
```

You'll also need Postgres reachable locally — `docker compose up -d postgres` starts just the
database container while you run the backend/frontend natively.

## Project structure

```
AiProject/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint
│   │   ├── database.py      # SQLAlchemy engine/session setup
│   │   ├── models.py        # ORM models (Todo, Note, TrackerRow, Document)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── crud.py          # Database CRUD helpers
│   │   ├── rag/             # RAG pipeline (ingestion, vector store, chain)
│   │   └── routers/         # API endpoints, grouped by resource
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── Home.py               # Dashboard entrypoint
│   ├── pages/                # Chatbot, Tracker, Todos, Notes
│   ├── api_client.py         # HTTP client wrapping the backend API
│   ├── sidebar.py            # Shared sidebar chrome
│   ├── stats.py              # Dashboard stat helpers
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .env.example
```

## Screenshots

### Home dashboard
![Home dashboard](docs/screenshots/home.png)

### AI Chatbot
![AI Chatbot](docs/screenshots/chatbot.png)

### To-do List
![To-do List](docs/screenshots/todos.png)

### Notes
![Notes](docs/screenshots/notes.png)

### Tracker
![Tracker](docs/screenshots/tracker.png)
