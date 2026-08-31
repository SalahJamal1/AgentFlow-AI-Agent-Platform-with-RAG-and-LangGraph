from langgraph.graph import StateGraph, END

from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import GradeHallucinations, hallucinations_grader
from graph.chains.router import RouteQuery, router
from graph.consts import RETRIEVE, WEBSEARCH, GRADE_DOCUMENTS, GENERATE
from graph.node.generate import generate
from graph.node.grader_documents import grader_documents
from graph.node.retriever_node import retriever_node
from graph.node.web_search import web_search
from graph.state import GraphState


def router_question(state: GraphState):
    print("---ROUTE QUESTION---")
    question = state["question"]
    source: RouteQuery = router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE


def decided_generate(state: GraphState):
    print("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        print(
            "---DECISION: NOT ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return WEBSEARCH
    else:
        print("---DECISION: GENERATE---")
        return GENERATE


def hallucinations(state: GraphState):
    print("---HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    score: GradeHallucinations = hallucinations_grader.invoke(
        {"documents": documents, "generation": generation}
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


builder = StateGraph(GraphState)
builder.set_conditional_entry_point(
    router_question, {WEBSEARCH: WEBSEARCH, RETRIEVE: RETRIEVE}
)
builder.add_node(RETRIEVE, retriever_node)
builder.add_node(GRADE_DOCUMENTS, grader_documents)
builder.add_node(WEBSEARCH, web_search)
builder.add_node(GENERATE, generate)

builder.add_edge(RETRIEVE, GRADE_DOCUMENTS)
builder.add_edge(WEBSEARCH, GENERATE)
builder.add_conditional_edges(
    GRADE_DOCUMENTS, decided_generate, {WEBSEARCH: WEBSEARCH, GENERATE: GENERATE}
)

builder.add_conditional_edges(
    GENERATE,
    hallucinations,
    {"useful": END, "not useful": WEBSEARCH, "not supported": GENERATE},
)

app_deep = builder.compile()
app_deep.get_graph().draw_mermaid_png(output_file_path="flow.png")
if __name__ == "__main__":
    res = app_deep.invoke({"question": "what is agent deep"})

    print(res)
