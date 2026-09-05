import streamlit as st

from sidebar import render_sidebar
from stats import get_document_count, get_open_todo_count, get_recent_notes

st.set_page_config(page_title="AiProject", page_icon="🤖", layout="wide")
render_sidebar()

st.title("🏠 Home")
st.caption("Quick overview of your workspace.")

col_todos, col_docs = st.columns(2)

with col_todos:
    try:
        st.metric("📋 Open Todos", get_open_todo_count())
    except Exception as exc:
        st.error(f"Could not load todos: {exc}")
    st.page_link("pages/3_Todos.py", label="Go to Todos", icon="➡️")

with col_docs:
    try:
        st.metric("📄 Documents Ingested", get_document_count())
    except Exception as exc:
        st.error(f"Could not load documents: {exc}")
    st.page_link("pages/1_Chatbot.py", label="Manage documents", icon="➡️")

st.divider()

st.subheader("📝 Recent Notes")
try:
    recent_notes = get_recent_notes(limit=5)
except Exception as exc:
    st.error(f"Could not load notes: {exc}")
    recent_notes = []

if not recent_notes:
    st.caption("No notes yet.")
else:
    for note in recent_notes:
        with st.container(border=True):
            st.markdown(f"**{note['title']}**")
            preview = note["content"].strip().splitlines()[0] if note["content"].strip() else "*Empty note*"
            st.caption(preview[:120])

st.page_link("pages/4_Notes.py", label="Go to Notes", icon="➡️")
