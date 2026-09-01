from dotenv import load_dotenv

load_dotenv()
from typing import Dict, Any

from langchain_tavily import TavilySearch

from graph.state import GraphState

tavily_search = TavilySearch(max_results=5)


def web_search(state: GraphState) -> Dict[str, Any]:
    print("--- WEB SEARCH ---")
    question = state["question"]
    documents: list[str] = state.get("documents", None)
    results = tavily_search.invoke(question)["results"]
    results_joined = "\n\n".join(result["content"] for result in results)

    if documents is not None:
        documents.append(results_joined)
    else:
        documents = [results_joined]
    websearch_count = state.get("websearch_count", 0) + 1
    return {"question": question, "documents": documents, "websearch_count": websearch_count}


if __name__ == "__main__":
    res = web_search(state={"question": "what is agent ?", "documents": None})
    print(res)
