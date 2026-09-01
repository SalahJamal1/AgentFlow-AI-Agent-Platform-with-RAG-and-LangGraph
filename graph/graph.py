import os

from langgraph.graph import StateGraph, END

from graph.chains.router import RouteQuery, router
from graph.consts import RETRIEVE, WEBSEARCH, GRADE_DOCUMENTS, GENERATE, MCP
from graph.node.chat_history_node import chat_history_node
from graph.node.generate import generate
from graph.node.grader_documents import grader_documents
from graph.node.retriever_node import retriever_node
from graph.node.web_search import web_search
from graph.state import GraphState
from graph.node.hallucination_node import hallucinations



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
    elif source.datasource == "mcp":
        print("---ROUTE QUESTION TO MCP---")
        return MCP


MAX_WEBSEARCH_RETRIES = 2


def decided_generate(state: GraphState):
    print("---ASSESS GRADED DOCUMENTS---")

    if state.get("web_search", False) and state.get("websearch_count", 0) < MAX_WEBSEARCH_RETRIES:
        print(
            "---DECISION: NOT ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return WEBSEARCH
    else:
        print("---DECISION: GENERATE---")
        return GENERATE



builder = StateGraph(GraphState)
builder.set_conditional_entry_point(
    router_question, {WEBSEARCH: WEBSEARCH, RETRIEVE: RETRIEVE,MCP: MCP}
)
builder.add_node(RETRIEVE, retriever_node)
builder.add_node(MCP,chat_history_node)
builder.add_node(WEBSEARCH, web_search)


builder.add_node(GRADE_DOCUMENTS, grader_documents)

builder.add_node(GENERATE, generate)

builder.add_edge(RETRIEVE, GRADE_DOCUMENTS)
builder.add_edge(WEBSEARCH, GRADE_DOCUMENTS)
builder.add_edge(MCP, GENERATE)

builder.add_conditional_edges(
    GRADE_DOCUMENTS, decided_generate, {WEBSEARCH: WEBSEARCH, GENERATE: GENERATE}
)

builder.add_conditional_edges(
    GENERATE,
    hallucinations,
    {"useful": END, "not useful": WEBSEARCH, "not supported": GENERATE},
)

app = builder.compile()
if __name__ == "__main__":
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    result = app.invoke(
        {
            "question": "give me road map for ai?",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzYWxhaEBleGFtcGxlLmNvbSIsImlkIjoxLCJleHAiOjE3ODgyMzQ1OTMsImlzcyI6ImFnZW50X2Zsb3ciLCJhdWQiOiJhZ2VudF9mbG93In0.uk-vNSgdWCFBdYmgMhEWUKgx05WUq513E6O-MaQtsZ8",
        }
    )
    print(result)
