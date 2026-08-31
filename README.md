# AgentFlow — AI Agent Platform with RAG and LangGraph

A FastAPI backend that pairs user/chat management with an adaptive **Retrieval-Augmented Generation (RAG)** agent built on **LangGraph**. Incoming questions are routed to either a local Chroma vector store or a live web search, graded for relevance, and checked for hallucinations before an answer is returned and persisted as chat history.

## Architecture

```
Question ──▶ router_question ──┬──▶ retrieve (Chroma vector store) ──▶ grade_documents ──┬──▶ generate ──▶ hallucination check
                                 │                                                          │        │
                                 └──▶ websearch (Tavily) ─────────────────────────────────▶ generate ◀┘
                                                                                             │
                                                                              not supported ─┘ (retry generate)
                                                                              not useful ──▶ websearch
                                                                              useful ──▶ END
```

- **Router** (`graph/chains/router.py`) — decides whether a question should be answered from the vector store or a fresh web search.
- **Retriever** (`graph/node/retriever_node.py`) — pulls relevant chunks from the local Chroma collection.
- **Grader** (`graph/node/grader_documents.py`) — filters retrieved documents for relevance; falls back to web search if none qualify.
- **Web search** (`graph/node/web_search.py`) — queries Tavily when the vector store is insufficient.
- **Generate** (`graph/node/generate.py`) — produces the answer from the selected context.
- **Hallucination grader** (`graph/node/hallucinations_node.py`) — verifies the answer is grounded and useful, looping back to `generate` or `websearch` when it isn't.

The compiled graph lives in `graph/graph.py` and is invoked directly from the `/api/v1/chats` endpoints.

## Tech stack

- **API**: FastAPI, Uvicorn
- **Agent orchestration**: LangGraph, LangChain
- **LLM / embeddings**: Ollama (`qwen3:1.7b`, `nomic-embed-text`) — swap for OpenAI/Google models via the corresponding LangChain integrations already included
- **Vector store**: Chroma (local, persisted to `chroma_db/`)
- **Web search**: Tavily
- **Database**: MySQL via SQLAlchemy, migrations with Alembic
- **Auth**: JWT (python-jose) with bcrypt password hashing
- **Package management**: [uv](https://github.com/astral-sh/uv)

## Project structure

```
app/                FastAPI application
├── main.py          App entrypoint, router registration
├── database.py       SQLAlchemy engine/session setup
├── models.py          ORM models (Users, Conversations, Messages)
├── schema.py           Pydantic request/response schemas
├── dependencies.py      Shared FastAPI dependencies (DB session)
├── alembic/               Database migrations
└── router/
    ├── auth.py            Register / login / JWT handling
    └── chats.py            Conversations & messages, invokes the LangGraph agent

graph/               LangGraph agent
├── graph.py          Graph definition (nodes, edges, routing logic)
├── state.py            Shared graph state + LLM instance
├── ingestion.py          Loads and indexes documents into Chroma
├── consts.py               Node name constants
├── node/                    Node implementations
└── chains/                   Router, generation, and grading chains
```

## Getting started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- A running MySQL server
- [Ollama](https://ollama.com) running locally with the `qwen3:1.7b` and `nomic-embed-text` models pulled (or swap in another provider)

### Setup

```bash
uv sync
```

Create a `.env` file in the project root with:

```env
SECRET_KEY=
ALGORITHM=
ISSUER=
AUDIENCE=

LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX=
```

By default the app connects to MySQL at `mysql+pymysql://root:2025@localhost:3306` and creates an `ai_agent_rag` database automatically (`app/database.py`); update the connection string there if your setup differs.

### Ingest documents into the vector store

```bash
uv run python -m graph.ingestion
```

This loads the default set of blog URLs (or a PDF path passed to `ingest()`), chunks them, and indexes them into the local Chroma collection at `chroma_db/`.

### Run the API

```bash
uv run uvicorn app.main:app --reload
```

### Run the agent standalone

```bash
uv run python -m graph.graph
```

## API overview

All routes are prefixed with `/api/v1`.

**Auth** (`/api/v1/auth`)
| Method | Path        | Description                  |
|--------|-------------|-------------------------------|
| POST   | `/register` | Create a new user             |
| POST   | `/login`    | Get a JWT access token        |

**Chats** (`/api/v1/chats`, requires `Authorization: Bearer <token>`)
| Method | Path                             | Description                            |
|--------|----------------------------------|-----------------------------------------|
| GET    | `/`                               | List the current user's conversations  |
| POST   | `/`                               | Create a new conversation              |
| GET    | `/{id}`                            | Get a conversation with its messages   |
| POST   | `/{conversation_id}/messages`       | Send a message, run the RAG agent, get the updated history |
| GET    | `/{conversation_id}/messages`        | Get a conversation's message history   |
