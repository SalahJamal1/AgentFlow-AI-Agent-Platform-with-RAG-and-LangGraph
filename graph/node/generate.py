from typing import Dict, Any

from graph.chains.generation import generation
from graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("--- GENERATE ---")
    question = state["question"]
    document = state["documents"]
    generation_results = generation.invoke({"question": question, "context": document})

    return {
        "question": question,
        "documents": document,
        "generation": generation_results,
    }


if __name__ == "__main__":
    res = generate(state={"question": "What is RL?", "documents": []})
    print(res)
