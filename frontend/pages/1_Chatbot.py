import json

import streamlit as st

from api_client import chat_stream, delete_document, get_documents, get_models, upload_document
from sidebar import render_sidebar

render_sidebar()

st.title("💬 AI Chatbot")

# ---------- Sidebar: document management + model switcher ----------
with st.sidebar:
    st.divider()
    st.subheader("Documents")

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "md"])
    if uploaded_file is not None and st.button("Ingest document"):
        try:
            with st.spinner("Ingesting document..."):
                upload_document(
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
            st.success(f"Ingested {uploaded_file.name}")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to ingest document: {exc}")

    try:
        documents = get_documents()
    except Exception as exc:
        st.error(f"Could not load documents: {exc}")
        documents = []

    if not documents:
        st.caption("No documents uploaded yet.")
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

prompt = st.chat_input("Ask something about your documents...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    sources_holder: list[str] = []

    def token_stream():
        for line in chat_stream(prompt, model=selected_model):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event["type"] == "token":
                yield event["content"]
            elif event["type"] == "sources":
                sources_holder.extend(event["sources"])

    with st.chat_message("assistant"):
        full_response = ""
        try:
            full_response = st.write_stream(token_stream())
        except Exception as exc:
            st.error(f"Chat failed: {exc}")
        if sources_holder:
            st.caption("📄 Sources: " + ", ".join(sources_holder))

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "sources": sources_holder}
    )
