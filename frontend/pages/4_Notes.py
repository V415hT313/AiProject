import streamlit as st

from api_client import create_note, delete_note, get_notes, update_note
from sidebar import render_sidebar

render_sidebar()

st.title("📝 Notes")

with st.form("new_note_form", clear_on_submit=True):
    st.subheader("New note")
    title = st.text_input("Title")
    content = st.text_area("Content (Markdown supported)", height=150)
    submitted = st.form_submit_button("Add")

    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            try:
                with st.spinner("Adding note..."):
                    create_note(title.strip(), content)
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to create note: {exc}")

st.divider()

try:
    with st.spinner("Loading notes..."):
        notes = get_notes()
except Exception as exc:
    st.error(f"Could not load notes: {exc}")
    notes = []

if not notes:
    st.caption("No notes yet — add one above.")
else:
    for note in notes:
        with st.expander(note["title"]):
            edit_col, preview_col = st.columns(2)

            with edit_col:
                st.caption("Edit")
                new_content = st.text_area(
                    "Content", value=note["content"], height=200, key=f"content_{note['id']}", label_visibility="collapsed"
                )

            with preview_col:
                st.caption("Preview")
                st.markdown(new_content or "*Nothing to preview*")

            save_col, delete_col = st.columns([1, 1])
            with save_col:
                if st.button("Save", key=f"save_{note['id']}"):
                    try:
                        with st.spinner("Saving..."):
                            update_note(note["id"], content=new_content)
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to save note: {exc}")
            with delete_col:
                if st.button("Delete", key=f"delete_{note['id']}"):
                    try:
                        with st.spinner("Deleting..."):
                            delete_note(note["id"])
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to delete note: {exc}")
