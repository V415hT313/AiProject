from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama

from .. import config
from .vectorstore import get_vectorstore

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using the provided context. "
    "If the context does not contain the answer, say you don't know. Be concise.\n\n"
    "Context:\n{context}"
)


def get_retriever(user_id: int, session_id: int, k: int = 4):
    return get_vectorstore().as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"$and": [{"user_id": user_id}, {"session_id": session_id}]},
        }
    )


def get_llm(model: str | None = None, streaming: bool = False) -> ChatOllama:
    return ChatOllama(
        model=model or config.CHAT_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        streaming=streaming,
    )


def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def to_lc_messages(history: list[dict]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))
    return messages


def build_rag_chain(user_id: int, session_id: int, model: str | None = None, streaming: bool = False):
    retriever = get_retriever(user_id=user_id, session_id=session_id)
    llm = get_llm(model=model, streaming=streaming)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )

    chain = (
        RunnablePassthrough.assign(
            context=lambda x: format_docs(retriever.invoke(x["question"]))
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever
