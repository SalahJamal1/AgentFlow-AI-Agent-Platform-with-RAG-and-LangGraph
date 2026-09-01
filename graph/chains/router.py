from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.state import llm


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "websearch","mcp"] = Field(
        description=(
            "Choose the best datasource for answering the user's question: "
            "vectorstore for knowledge-base documents, "
            "websearch for current/general internet information, "
            "or mcp for user-specific data such as chat history."
        )
    )


llm_with_structured = llm.with_structured_output(RouteQuery)

system = """
You are an expert query router.

Choose exactly one datasource:

1. vectorstore
   Use this when the question is about information contained in the
   application's knowledge base, such as:
   - AI agents
   - prompt engineering
   - adversarial attacks
   - uploaded documents
   - other indexed knowledge-base content

2. websearch
   Use this when the question requires:
   - current information
   - recent events
   - internet information
   - information not available in the knowledge base

3. mcp
   Use this when the question requires user-specific or application data,
   especially:
   - previous conversations
   - chat history
   - user's conversations
   - user's application data
   - data retrieved through backend APIs

Examples:

"What is prompt engineering?"
→ vectorstore

"What are the latest AI agent frameworks?"
→ websearch

"What did I ask you yesterday?"
→ mcp

"Show me my previous conversations"
→ mcp

"What did we discuss about LangGraph?"
→ mcp

"Explain adversarial attacks"
→ vectorstore
"""
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{question}")])

router = prompt | llm_with_structured
