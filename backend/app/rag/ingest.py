import pathlib

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .vectorstore import get_vectorstore

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def load_documents(file_path: str):
    ext = pathlib.Path(file_path).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path).load()
    if ext in {".txt", ".md"}:
        return TextLoader(file_path, encoding="utf-8").load()
    raise ValueError(f"Unsupported file type: {ext}")


def ingest_file(file_path: str, doc_id: int, filename: str, user_id: int) -> int:
    documents = load_documents(file_path)
    chunks = _splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["source"] = filename
        chunk.metadata["user_id"] = user_id

    if chunks:
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        get_vectorstore().add_documents(chunks, ids=ids)

    return len(chunks)


def delete_document_vectors(doc_id: int, user_id: int) -> None:
    vectorstore = get_vectorstore()
    vectorstore._collection.delete(where={"$and": [{"doc_id": doc_id}, {"user_id": user_id}]})
