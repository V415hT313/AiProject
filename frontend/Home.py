import streamlit as st

from auth_ui import require_login
from sidebar import render_sidebar
from stats import get_document_count, get_open_todo_count, get_recent_notes

st.set_page_config(page_title="R2D2", page_icon="🤖", layout="wide")
require_login()
render_sidebar()

st.title("🏠 Home")
st.caption("Quick overview of your workspace.")

with st.spinner("Loading dashboard..."):
    open_todos = todos_error = None
    doc_count = docs_error = None
    recent_notes = notes_error = None

    try:
        open_todos = get_open_todo_count()
    except Exception as exc:
        todos_error = str(exc)

    try:
        doc_count = get_document_count()
    except Exception as exc:
        docs_error = str(exc)

    try:
        recent_notes = get_recent_notes(limit=5)
    except Exception as exc:
        notes_error = str(exc)

col_todos, col_docs = st.columns(2)

with col_todos:
    if todos_error:
        st.error(f"Could not load todos: {todos_error}")
    else:
        st.metric("📋 Open Todos", open_todos)
    st.page_link("pages/3_Todos.py", label="Go to Todos", icon="➡️")

with col_docs:
    if docs_error:
        st.error(f"Could not load documents: {docs_error}")
    else:
        st.metric("📄 Documents Ingested", doc_count)
    st.page_link("pages/1_Chatbot.py", label="Manage documents", icon="➡️")

st.divider()

st.subheader("📝 Recent Notes")
if notes_error:
    st.error(f"Could not load notes: {notes_error}")
elif not recent_notes:
    st.caption("No notes yet.")
else:
    for note in recent_notes:
        with st.container(border=True):
            st.markdown(f"**{note['title']}**")
            preview = note["content"].strip().splitlines()[0] if note["content"].strip() else "*Empty note*"
            st.caption(preview[:120])

st.page_link("pages/4_Notes.py", label="Go to Notes", icon="➡️")
