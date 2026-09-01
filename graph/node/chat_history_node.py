from graph.mcp.mcp_api import get_chat_history
from graph.state import GraphState


def chat_history_node(state: GraphState) -> GraphState:
    access_token = state.get("access_token")

    if not access_token:
        return {**state, "chat_history": []}

    try:
        chat_history = get_chat_history(access_token)
    except ValueError:
        chat_history = []

    return {**state, "chat_history": chat_history}
