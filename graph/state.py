from typing import TypedDict, NotRequired

from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:1.7b")


class GraphState(TypedDict):
    question: NotRequired[str]
    access_token: NotRequired[str]
    chat_history: NotRequired[str]
    web_search: NotRequired[bool]
    generation: NotRequired[str]
    documents: NotRequired[list[str]]
    retry_count: NotRequired[int]
    websearch_count: NotRequired[int]
