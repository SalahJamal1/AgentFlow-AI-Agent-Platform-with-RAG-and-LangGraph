from typing import Dict, Any

from graph.ingestion import retriever
from graph.state import GraphState


def retriever_node(state: GraphState) -> Dict[str, Any]:
    print("--- Retriever ---")
    question = state["question"]
    document = retriever.invoke(question, k=5)
    return {"question": question, "documents": document}


if __name__ == "__main__":
    res = retriever_node(state={"question": "What is your favorite language?"})
    print(res)
