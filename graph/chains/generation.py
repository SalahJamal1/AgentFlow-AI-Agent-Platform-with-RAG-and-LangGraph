from langchain_core.output_parsers import StrOutputParser
from langsmith import Client

from graph.state import llm

client = Client()
prompt = client.pull_prompt(
    "rlm/rag-prompt",
    dangerously_pull_public_prompt=True,
)

generation = prompt | llm | StrOutputParser()
