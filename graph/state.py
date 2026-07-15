from typing import TypedDict

from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:1.7b")


class GraphState(TypedDict):
    question: str
    web_search: bool
    generation: str
    documents: list[str]
    retry_count: int
