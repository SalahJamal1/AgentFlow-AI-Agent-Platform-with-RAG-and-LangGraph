from typing import Dict, Any

from graph.chains.generation import generation
from graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("--- GENERATE ---")
    question = state["question"]
    documents = state.get("documents",[])
    chat_history = state.get("chat_history",[])


    context_parts=[]
    if documents:
        context_parts.append(
            "Relevant documents:\n" +
            "\n\n".join(str(doc) for doc in documents)
        )

    if chat_history:
        context_parts.append(
            "Chat history:\n" +
            "\n\n".join(str(message) for message in chat_history)
        )
    context="\n\n".join(context_parts)
    generation_results = generation.invoke({"question": question, "context": context})
    retry_count=state.get("retry_count",0)+1
    return {
        **state,
        "retry_count": retry_count,
        "generation": generation_results,
    }


if __name__ == "__main__":
    res = generate(state={"question": "What is RL?", "documents": []})
    print(res)
