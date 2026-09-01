from graph.state import GraphState
from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import GradeHallucinations, hallucinations_grader

def hallucinations(state: GraphState):
    print("---HALLUCINATIONS---")
    question = state["question"]
    chat_history = state.get("chat_history",[])
    documents = state.get("documents",[])
    generation = state["generation"]
    retry_count=state["retry_count"]
    context_parts = []
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
    context = "\n\n".join(context_parts)
    if retry_count>=3:
        print("---Max Retries---")
        return "useful"
    score: GradeHallucinations = hallucinations_grader.invoke(
        {"documents": context, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"

