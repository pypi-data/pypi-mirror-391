import os
from tqdm import tqdm
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from core.embeddings import get_embeddings
from config.settings import CHROMA_DIR
import unicodedata
from chromadb import PersistentClient

def load_pdfs_from_folder(folder_path):
    """Load all PDF files from a directory."""
    docs = []
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    print(f"📂 Found {len(pdf_files)} PDF files in: {folder_path}\n")
    for filename in tqdm(pdf_files, desc="📄 Loading PDFs"):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            try:
                loader = PyPDFLoader(file_path)
                file_docs = loader.load()
                for d in file_docs:
                    d.metadata["source"] = filename  # keep filename as source
                docs.extend(file_docs)
            except Exception as e:
                print(f"⚠️ Skipped {filename} due to error: {e}")
    print(f"✅ Loaded {len(docs)} documents from {folder_path}")
    return docs

def clean_text(text: str) -> str:
    """Remove invalid UTF-8 and normalize text."""
    if not isinstance(text, str):
        text = str(text)
    # Normalize combined unicode forms (e.g. accents, fullwidth chars)
    text = unicodedata.normalize("NFKC", text)
    # Strip out illegal surrogate pairs or undecodable bytes
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")


def build_chroma_db_from_folder(pdf_folder):
    """Build a Chroma database from all PDFs in a folder."""
    docs = load_pdfs_from_folder(pdf_folder)
    if not docs:
        raise ValueError("No PDFs found in folder!")
    
    # Split into chunks for embeddings
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    print(f"Split into {len(split_docs)} text chunks for embedding.")

    # 🔧 Clean text chunks before embedding
    print("🧹 Cleaning text for UTF-8 compatibility...")
    cleaned_docs = []
    for d in tqdm(split_docs, desc="Cleaning text"):
        try:
            d.page_content = clean_text(d.page_content)
            cleaned_docs.append(d)
        except Exception as e:
            print(f"⚠️ Skipped chunk from {d.metadata.get('source', 'unknown')}: {e}")
    print(f"✅ Cleaned {len(cleaned_docs)} chunks successfully.")



    # Embed and save into Chroma
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(cleaned_docs, embeddings, persist_directory=CHROMA_DIR, collection_name="bioimage_segmentation")
    vectordb.persist()
    print(f"💾 Chroma database saved to: {CHROMA_DIR}")
    return vectordb

# create a test query
def query_test():
    query = "computer vision for image segmentation"
    k = 5
    vectorstore = Chroma(collection_name="bioimage_segmentation", persist_directory=CHROMA_DIR, embedding_function = get_embeddings())
    results = vectorstore._similarity_search_with_relevance_scores(query, k=k)
    print(f"\n🔍 Query: {query}")
    print(f"📚 Top {k} retrieved documents:\n")
    for i, (doc, score) in enumerate(results, start=1):
        snippet = doc.page_content[:200].replace("\n", " ")
        print(f"--- Result {i} ---")
        print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Relevance: {score:.3f}")
        print(f"Text: {snippet}...\n")
    return

def list_chroma_collections():
    """List all collections stored in the Chroma persistence directory."""
    print(f"🔍 Listing collections in {CHROMA_DIR}")
    client = PersistentClient(path=CHROMA_DIR)
    collections = client.list_collections()

    if not collections:
        print("⚠️ No collections found in the Chroma directory.")
    else:
        for c in collections:
            print(f"📚 {c.name}")
    return collections

def main():
    #build_chroma_db_from_folder("data/papers")
    query_test()
    list_chroma_collections()
    return

if __name__ == "__main__":
    main()