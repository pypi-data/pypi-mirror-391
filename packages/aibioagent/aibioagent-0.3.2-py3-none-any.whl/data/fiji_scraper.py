"""
data/fiji_scraper.py
--------------------
Scrapes official Fiji tutorials and documentation into a local vector DB.
"""

import os
from typing import List
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from core.embeddings import get_embeddings
from config.settings import CHROMA_DIR
import unicodedata
from chromadb import PersistentClient


# Official Fiji documentation URLs plus others
# rightnow github weblink doesnt work
TECH_ROOT_URLS = [
    "https://imagej.net/learn",
    "https://imagej.net/plugins",
    "https://imagej.net/tutorials",
    "https://imagej.net/imaging",
    "https://scikit-image.org/docs/stable/",
    "https://scikit-image.org/docs/stable/user_guide/index.html",
    "https://scikit-image.org/docs/stable/auto_examples/index.html",
    "https://scikit-image.org/docs/stable/api/api.html",
    "https://docs.opencv.org/4.x/index.html",
    "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html",
    "https://pillow.readthedocs.io/en/stable/",
    "https://pillow.readthedocs.io/en/stable/reference/index.html",
    "https://api.python.langchain.com/en/latest/langchain_api_reference.html#",
    "https://api.python.langchain.com/en/latest/core_api_reference.html",
    "https://api.python.langchain.com/en/latest/community_api_reference.html", 
    "https://api.python.langchain.com/en/latest/experimental_api_reference.html",
    "https://api.python.langchain.com/en/latest/text_splitters_api_reference.html",
    
]
MAX_LINKS_PER_ROOT = 300  # prevent overload
COLLECTION_NAME = "online_tech_docs"

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Remove invalid UTF-8 and normalize text."""
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFKC", text)
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")

def crawl_fiji_links(base_url):
    """Extract all internal Fiji links from a page."""
    try:
        resp = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"⚠️ Failed to fetch {base_url}: {e}")
        return []

    base_domain = urlparse(base_url).netloc
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == base_domain and full_url.startswith("https://imagej.net/"):
            if "#" not in full_url and "?" not in full_url:
                links.add(full_url)

    ans = sorted(list(links))[:MAX_LINKS_PER_ROOT]
    #print(ans)
    return ans

def crawl_dynamic_links(url):
    """Extract sub-links from JS-rendered pages like scikit-image docs."""
    links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        anchors = page.query_selector_all("a[href]")
        for a in anchors:
            href = a.get_attribute("href")
            if href and href.endswith(".html"):
                links.add(urljoin(url, href))
        browser.close()
    return sorted(links)

def load_webpages(urls):
    """Load webpages as LangChain documents."""
    docs = []
    for url in tqdm(urls, desc="🌐 Loading Web pages"):
        try:
            loader = WebBaseLoader(url)
            loader.requests_kwargs = {'verify':False}
            web_docs = loader.load()
            for d in web_docs:
                d.metadata["source"] = url
            docs.extend(web_docs)
        except Exception as e:
            print(f"⚠️ Skipped {url}: {e}")
    print(f"✅ Loaded {len(docs)} documents total.")
    return docs

# ---------------------------------------------------------------------
# Build Chroma DB - Generic Function for Any URLs
# ---------------------------------------------------------------------
def scrape_and_build_db(
    root_urls: List[str],
    collection_name: str = "online_tech_docs",
    max_links_per_root: int = 300,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    verbose: bool = True
):
    """
    Scrape web documentation from URLs and build a Chroma database.
    
    Parameters
    ----------
    root_urls : list of str
        List of URLs to scrape
    collection_name : str
        Name for the Chroma collection
    max_links_per_root : int
        Maximum number of links to crawl per root URL
    chunk_size : int
        Text chunk size for embeddings
    chunk_overlap : int
        Overlap between chunks
    verbose : bool
        Print progress information
    """
    if verbose:
        print(f"🔍 Starting documentation crawl for {len(root_urls)} root URL(s)...")
    
    all_links = set(root_urls)
    
    # Crawl sub-links from each root
    for root in root_urls:
        try:
            if "imagej" in root:
                sub_links = crawl_fiji_links(root)
            else:
                sub_links = crawl_dynamic_links(root)
            
            # Limit number of links
            sub_links = list(sub_links)[:max_links_per_root]
            all_links.update(sub_links)
            
            if verbose:
                print(f"• Found {len(sub_links)} sub-links under {root}")
        except Exception as e:
            if verbose:
                print(f"⚠️  Error crawling {root}: {e}")
    
    if verbose:
        print(f"✅ Total pages to process: {len(all_links)}")
    
    # Load all pages
    docs = load_webpages(sorted(all_links))
    if not docs:
        raise ValueError("❌ No documentation pages loaded!")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = splitter.split_documents(docs)
    
    if verbose:
        print(f"✂️  Split into {len(split_docs)} text chunks.")
    
    # Clean text
    cleaned_docs = []
    iterator = tqdm(split_docs, desc="🧹 Cleaning text") if verbose else split_docs
    for d in iterator:
        try:
            d.page_content = clean_text(d.page_content)
            cleaned_docs.append(d)
        except Exception as e:
            if verbose:
                print(f"⚠️  Skipped chunk: {e}")
    
    if verbose:
        print(f"✅ Cleaned {len(cleaned_docs)} chunks successfully.")
    
    # Build embeddings and store
    if verbose:
        print("🔢 Generating embeddings and saving to Chroma...")
    
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        cleaned_docs,
        embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=collection_name,
    )
    vectordb.persist()
    
    if verbose:
        print(f"💾 Knowledge base saved to: {CHROMA_DIR}")
    
    return vectordb


# ---------------------------------------------------------------------
# Build Chroma DB - Fiji Specific (Legacy)
# ---------------------------------------------------------------------
def build_chroma_db_from_fiji():
    """Scrape official Fiji docs and store embeddings in Chroma."""
    print("🔍 Starting Fiji documentation crawl...")
    all_links = set(TECH_ROOT_URLS)

    # crawl sub-links
    for root in TECH_ROOT_URLS:
        if "imagej" in root:
            sub_links = crawl_fiji_links(root)
        else:
            sub_links = crawl_dynamic_links(root)
        all_links.update(sub_links)
        print(f"• Found {len(sub_links)} sub-links under {root}")

    print(f"✅ Total pages to process: {len(all_links)}")
    # Load all pages as LangChain documents
    docs = load_webpages(sorted(all_links))
    if not docs:
        raise ValueError("❌ No documentation pages loaded!")
    # Split into text chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    print(f"✂️ Split into {len(split_docs)} text chunks.")
    # Clean text
    cleaned_docs = []
    for d in tqdm(split_docs, desc="🧹 Cleaning text"):
        try:
            d.page_content = clean_text(d.page_content)
            cleaned_docs.append(d)
        except Exception as e:
            print(f"⚠️ Skipped chunk from {d.metadata.get('source', 'unknown')}: {e}")
    print(f"✅ Cleaned {len(cleaned_docs)} chunks successfully.")
    # Build embeddings and store
    print("🔢 Generating embeddings and saving to Chroma...")
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        cleaned_docs,
        embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
    )
    vectordb.persist()
    print(f"💾 Fiji knowledge base saved to: {CHROMA_DIR}")
    return vectordb

# create a test query
def query_test():
    query = "Fiji gaussian"
    k = 5
    vectorstore = Chroma(collection_name=COLLECTION_NAME, persist_directory=CHROMA_DIR, embedding_function = get_embeddings())
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
# ---------------------------------------------------------------------
# Main Entry
# ---------------------------------------------------------------------
def main():
    # Uncomment to rebuild the database
    build_chroma_db_from_fiji()
    #query_test()
    #list_chroma_collections()
    return

if __name__ == "__main__":
    main()
