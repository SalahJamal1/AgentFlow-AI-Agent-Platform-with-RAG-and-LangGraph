from graph.chains.answer_grader import answer_grader,GradeAnswer
from graph.chains.hallucination_grader import GradeHallucinations, hallucinations_grader
from graph.state import GraphState

def hallucinations(state: GraphState):
    print("---HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    retry_count=state["retry_count"]
    if retry_count > 3:
        return "useful"

    score: GradeHallucinations = hallucinations_grader.invoke( # type: ignore
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score:GradeAnswer = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
