from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama

from .. import config
from .vectorstore import get_vectorstore

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using the provided context. "
    "If the context does not contain the answer, say you don't know. Be concise.\n\n"
    "Context:\n{context}"
)


def get_retriever(k: int = 4):
    return get_vectorstore().as_retriever(search_kwargs={"k": k})


def get_llm(model: str | None = None, streaming: bool = False) -> ChatOllama:
    return ChatOllama(
        model=model or config.CHAT_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        streaming=streaming,
    )


def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(model: str | None = None, streaming: bool = False):
    retriever = get_retriever()
    llm = get_llm(model=model, streaming=streaming)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{question}")]
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever
