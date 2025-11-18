from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config.settings import OPENAI_API_KEY, EMBED_MODEL, CHROMA_DIR

def get_embeddings():
    """Initialize OpenAI embedding model."""
    return OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY, max_retries=10)

def get_vectorstore(collection_name='test'):
    """Load (or create empty) ChromaDB vectorstore."""
    embeddings = get_embeddings()
    vectordb = Chroma(collection_name = collection_name, persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return vectordb

def main():
    emb = get_embeddings()
    vector = emb.embed_query("deep learning microscopy image analysis")
    print("Embedding vector length:", len(vector))
    print("Example values:", vector[:10])
    vectordb = get_vectorstore()
    print("💾 Loaded Chroma directory:", CHROMA_DIR)

def list_collections():
    chroma = Chroma(persist_directory=CHROMA_DIR)
    print("Collections:", chroma._client.list_collections())

if __name__ == "__main__":
    list_collections()
