import json

import streamlit as st

from api_client import (
    chat_stream,
    create_chat_session,
    create_note,
    delete_chat_session,
    delete_document,
    get_chat_session_messages,
    get_chat_sessions,
    get_documents,
    get_models,
    upload_document,
)
from auth_ui import require_login
from sidebar import render_sidebar

require_login()
render_sidebar()

st.title("💬 AI Chatbot")

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = None


def _load_session(session_id: int) -> None:
    try:
        messages = get_chat_session_messages(session_id)
    except Exception as exc:
        st.error(f"Could not load chat: {exc}")
        return
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "sources": m.get("sources", [])} for m in messages
    ]
    st.session_state.chat_session_id = session_id


# ---------- Sidebar: chat history, document library, model switcher ----------
with st.sidebar:
    st.divider()
    st.subheader("Chats")

    if st.button("➕ New Chat", width="stretch"):
        st.session_state.messages = []
        st.session_state.chat_session_id = None
        st.rerun()

    try:
        sessions = get_chat_sessions()
    except Exception as exc:
        st.error(f"Could not load chat history: {exc}")
        sessions = []

    if not sessions:
        st.caption("No past chats yet.")
    else:
        for sess in sessions:
            is_active = sess["id"] == st.session_state.chat_session_id
            title_col, delete_col = st.columns([4, 1])
            with title_col:
                label = ("🟢 " if is_active else "") + sess["title"]
                if st.button(label, key=f"session_{sess['id']}", width="stretch"):
                    _load_session(sess["id"])
                    st.rerun()
            with delete_col:
                if st.button("🗑️", key=f"delete_session_{sess['id']}"):
                    try:
                        delete_chat_session(sess["id"])
                        if is_active:
                            st.session_state.messages = []
                            st.session_state.chat_session_id = None
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to delete chat: {exc}")

    st.divider()
    st.subheader("Documents in this chat")

    if st.session_state.chat_session_id is None:
        st.caption("Start typing or attach a document below to begin a chat.")
        documents = []
    else:
        try:
            documents = get_documents(st.session_state.chat_session_id)
        except Exception as exc:
            st.error(f"Could not load documents: {exc}")
            documents = []

    if st.session_state.chat_session_id is not None and not documents:
        st.caption("No documents in this chat yet — attach one from the message box below.")
    if documents:
        for doc in documents:
            doc_col, delete_col = st.columns([4, 1])
            with doc_col:
                st.caption(f"{doc['filename']} ({doc['num_chunks']} chunks)")
            with delete_col:
                if st.button("🗑️", key=f"delete_doc_{doc['id']}"):
                    try:
                        delete_document(doc["id"])
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed to delete document: {exc}")

    st.divider()
    st.subheader("Model")
    try:
        models = get_models()
    except Exception as exc:
        st.error(f"Could not load models: {exc}")
        models = []

    if models:
        selected_model = st.selectbox("Model", models, label_visibility="collapsed")
    else:
        selected_model = None
        st.caption("No chat models found — is Ollama running?")

# ---------- Main chat area ----------
if st.session_state.messages:
    if st.button("💾 Save chat as note"):
        first_user_msg = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"), "Chat"
        )
        title = "Chat: " + (first_user_msg[:50] + "..." if len(first_user_msg) > 50 else first_user_msg)
        transcript = "\n\n---\n\n".join(
            f"**{m['role'].capitalize()}:** {m['content']}" for m in st.session_state.messages
        )
        try:
            create_note(title, transcript)
            st.success("Saved as a new note — this is a snapshot and won't update as the chat continues.")
        except Exception as exc:
            st.error(f"Failed to save note: {exc}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("📄 Sources: " + ", ".join(msg["sources"]))

user_input = st.chat_input(
    "Ask something, or attach a document (PDF/TXT/MD)...",
    accept_file="multiple",
    file_type=["pdf", "txt", "md", "png", "jpg", "jpeg"],
)

if user_input:
    prompt = user_input.text
    attached_files = user_input.files

    if attached_files and st.session_state.chat_session_id is None:
        try:
            st.session_state.chat_session_id = create_chat_session()["id"]
        except Exception as exc:
            st.error(f"Could not start a new chat for this document: {exc}")
            attached_files = []

    for f in attached_files:
        ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if ext in IMAGE_EXTENSIONS:
            st.warning(
                f"Image support isn't implemented yet — skipped **{f.name}**. "
                "Only PDF/TXT/MD documents can be ingested for now."
            )
            continue
        try:
            with st.spinner(f"Ingesting {f.name}..."):
                upload_document(
                    f.name,
                    f.getvalue(),
                    f.type or "application/octet-stream",
                    st.session_state.chat_session_id,
                )
            st.success(f"Ingested {f.name}")
        except Exception as exc:
            st.error(f"Failed to ingest {f.name}: {exc}")

    if attached_files and not prompt:
        st.rerun()

    if prompt:
        # capture prior turns before appending this new one, so the model gets
        # the conversation-so-far as context (capped to keep the prompt bounded)
        history_payload = [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-20:]
        ]

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        sources_holder: list[str] = []
        error_holder: list[str] = []
        session_id_holder: list[int] = []

        def token_stream():
            for line in chat_stream(
                prompt,
                model=selected_model,
                history=history_payload,
                session_id=st.session_state.chat_session_id,
            ):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event["type"] == "token":
                    yield event["content"]
                elif event["type"] == "sources":
                    sources_holder.extend(event["sources"])
                elif event["type"] == "session":
                    session_id_holder.append(event["session_id"])
                elif event["type"] == "error":
                    error_holder.append(event["message"])

        with st.chat_message("assistant"):
            full_response = ""
            try:
                full_response = st.write_stream(token_stream())
            except Exception as exc:
                error_holder.append(str(exc))
            if error_holder:
                st.error(error_holder[0])
            if sources_holder:
                st.caption("📄 Sources: " + ", ".join(sources_holder))

        if session_id_holder:
            st.session_state.chat_session_id = session_id_holder[0]

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response, "sources": sources_holder}
        )
        st.rerun()
