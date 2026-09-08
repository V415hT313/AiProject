import streamlit as st

from api_client import create_todo, delete_todo, get_todos, update_todo
from auth_ui import require_login
from sidebar import render_sidebar

require_login()
render_sidebar()

st.title("✅ To-do List")

PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

with st.form("new_todo_form", clear_on_submit=True):
    st.subheader("Add a todo")
    title = st.text_input("Title")
    description = st.text_area("Description (optional)", height=80)
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
    submitted = st.form_submit_button("Add")

    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            try:
                with st.spinner("Adding todo..."):
                    create_todo(title.strip(), description.strip() or None, priority)
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to create todo: {exc}")

st.divider()

try:
    with st.spinner("Loading todos..."):
        todos = get_todos()
except Exception as exc:
    st.error(f"Could not load todos: {exc}")
    todos = []

if not todos:
    st.caption("No todos yet — add one above.")
else:
    todos_sorted = sorted(todos, key=lambda t: (t["done"], PRIORITY_ORDER.get(t["priority"], 9)))
    for todo in todos_sorted:
        col_check, col_body, col_delete = st.columns([0.6, 8, 1])

        with col_check:
            new_done = st.checkbox(
                "Done", value=todo["done"], key=f"done_{todo['id']}", label_visibility="collapsed"
            )
            if new_done != todo["done"]:
                try:
                    with st.spinner("Updating..."):
                        update_todo(todo["id"], done=new_done)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to update todo: {exc}")

        with col_body:
            emoji = PRIORITY_COLOR.get(todo["priority"], "⚪")
            strike = "~~" if todo["done"] else ""
            st.markdown(f"{emoji} {strike}**{todo['title']}**{strike}")
            if todo["description"]:
                st.caption(todo["description"])

        with col_delete:
            if st.button("🗑️", key=f"delete_{todo['id']}"):
                try:
                    with st.spinner("Deleting..."):
                        delete_todo(todo["id"])
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to delete todo: {exc}")
