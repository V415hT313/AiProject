import json

import streamlit as st

from api_client import chat_stream, delete_document, get_documents, get_models, upload_document
from auth_ui import require_login
from sidebar import render_sidebar

require_login()
render_sidebar()

st.title("💬 AI Chatbot")

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

# ---------- Sidebar: document library + model switcher ----------
with st.sidebar:
    st.divider()
    st.subheader("Documents")

    try:
        documents = get_documents()
    except Exception as exc:
        st.error(f"Could not load documents: {exc}")
        documents = []

    if not documents:
        st.caption("No documents yet — attach one from the message box below.")
    else:
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
if "messages" not in st.session_state:
    st.session_state.messages = []

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
                upload_document(f.name, f.getvalue(), f.type or "application/octet-stream")
            st.success(f"Ingested {f.name}")
        except Exception as exc:
            st.error(f"Failed to ingest {f.name}: {exc}")

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

        def token_stream():
            for line in chat_stream(prompt, model=selected_model, history=history_payload):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event["type"] == "token":
                    yield event["content"]
                elif event["type"] == "sources":
                    sources_holder.extend(event["sources"])
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

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response, "sources": sources_holder}
        )
