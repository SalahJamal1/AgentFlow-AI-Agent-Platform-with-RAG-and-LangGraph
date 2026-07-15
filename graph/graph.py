from langgraph.graph import StateGraph

from graph.chains.router import router, RouteQuery
from graph.consts import RETRIEVE, WEBSEARCH, GENERATE
from graph.node.generate import generate
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


builder = StateGraph(GraphState)
builder.set_conditional_entry_point(
    router_question, {WEBSEARCH: WEBSEARCH, RETRIEVE: RETRIEVE}
)

builder.add_node(RETRIEVE, retriever_node)
builder.add_node(WEBSEARCH, web_search)
builder.add_node(GENERATE, generate)

builder.add_edge(RETRIEVE, GENERATE)
builder.add_edge(WEBSEARCH, GENERATE)

app = builder.compile()
app.get_graph().draw_mermaid_png(output_file_path="flow_2.png")
if __name__ == "__main__":
    res = app.invoke({"question": "what is agent deep"})

    print(res)
