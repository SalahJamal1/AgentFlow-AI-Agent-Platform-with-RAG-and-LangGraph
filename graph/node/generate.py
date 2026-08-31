from typing import Dict, Any

from graph.chains.generation import generation
from graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("--- GENERATE ---")
    question = state["question"]
    document = state["documents"]
    retry_count=state.get("retry_count",0)+1
    generation_results = generation.invoke({"question": question, "context": document})

    return {
        "generation": generation_results,
        "retry_count": retry_count
    }


if __name__ == "__main__":
    res = generate(state={"question": "What is RL?", "documents": []})
    print(res)
