from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, chunk_overlap=100
)
embedding = OllamaEmbeddings(model="nomic-embed-text")
vector_store = Chroma(
    persist_directory="chroma_db", collection_name="rag", embedding_function=embedding
)