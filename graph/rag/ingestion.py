import asyncio
import hashlib

from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_core.documents import Document

from graph.rag.vector_store import vector_store,splitter

urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]


def document_idx(document:Document) -> str:
    page=document.metadata.get("page")
    source=document.metadata.get("source")
    page_content=document.page_content

    return hashlib.sha256(f"{source}:{page}:{page_content}".encode("utf-8")).hexdigest()

def web_loader() -> list[Document]:
    sub_list = [WebBaseLoader(url).load() for url in urls]
    documents = [item for sublist in sub_list for item in sublist]
    return documents


async def index_document(documents: list[Document]) -> None:
    batches: list[list[Document]] = [
        documents[i : i + 50] for i in range(0, len(documents), 50)
    ]

    async def add_batch(batch: list[Document], num_batch: int) -> bool:
        try:
            ids=[document_idx(document) for document in batch]
            await vector_store.aadd_documents(batch,ids)
            return True
        except Exception as e:
            print(f"Vector store error: batch {num_batch} - {e}")
            return False

    tasks = [add_batch(batch, num_batch) for num_batch, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for result in results if result)
    if successful == len(batches):
        print(
            f"Vector Store: Successfully Proced {successful}/{len(batches)} documents"
        )
    else:
        print(
            f"Vector Store: Failed to Proced {len(batches) - successful}/{len(batches)} documents"
        )
    return None


async def ingest(destination: str | None = None) -> None:
    documents: list[Document] = []
    if destination is None:
        documents = web_loader()
    else:
        documents = PyPDFLoader(destination).load()
    chunks: list[Document] = splitter.split_documents(documents)
    print(f"Processing {len(chunks)} chunks out of {len(documents)}")
    print("Start ingesting")

    await index_document(chunks)


if __name__ == "__main__":
    asyncio.run(ingest())
