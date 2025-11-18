"""
aibioagent.py
=============
User-facing API for the AI Bio Agent package.

This module provides simple functions for users to:
1. Configure their OpenAI API key
2. Add PDF papers to build custom knowledge bases
3. Add web URLs to scrape online documentation
4. Query the agents directly
5. Manage vector databases (collections)

The agents automatically search across ALL user-created collections,
so you don't need to worry about specifying which database to use.

Quick Start:
-----------
    import aibioagent as aba
    
    # Set up API key
    aba.set_api_key("sk-your-key-here")
    
    # Add papers to knowledge base
    aba.add_papers("path/to/pdfs", collection="my_research")
    
    # Add web documentation
    aba.add_urls(["https://docs.example.com"], collection="web_docs")
    
    # Query - automatically searches ALL collections
    response = aba.ask("What is adaptive optics?")
    print(response)
"""

import os
from typing import List, Optional, Union
from pathlib import Path


# ============================================================================
# 1. API Key Management
# ============================================================================

def set_api_key(api_key: str, save_to_env: bool = True) -> None:
    """
    Set OpenAI API key for the session.
    
    Parameters
    ----------
    api_key : str
        Your OpenAI API key (starts with 'sk-')
    save_to_env : bool, default=True
        If True, saves the key to .env file in current directory
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> aba.set_api_key("sk-your-key-here")
    ✅ API key set successfully!
    """
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("Invalid API key format. Should start with 'sk-'")
    
    # Set for current session
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Save to .env file
    if save_to_env:
        env_path = Path.cwd() / ".env"
        
        # Read existing .env if it exists
        existing_lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                existing_lines = [line for line in f.readlines() 
                                if not line.startswith("OPENAI_API_KEY=")]
        
        # Write back with new API key
        with open(env_path, "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.writelines(existing_lines)
        
        print(f"✅ API key set and saved to {env_path}")
    else:
        print("✅ API key set for current session only")


def get_api_key() -> Optional[str]:
    """
    Get the current OpenAI API key.
    
    Returns
    -------
    str or None
        The API key if set, None otherwise
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> key = aba.get_api_key()
    >>> print(f"Key: {key[:10]}...")  # Show first 10 chars
    """
    import os
    # Always read from current environment (includes .env loaded values)
    return os.getenv("OPENAI_API_KEY")


# ============================================================================
# 2. Model Configuration
# ============================================================================

def set_llm_model(model_name: str) -> None:
    """
    Set the LLM model for text generation.
    
    Parameters
    ----------
    model_name : str
        OpenAI model name (e.g., 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo')
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> aba.set_llm_model("gpt-4o")
    ✅ LLM model set to: gpt-4o
    
    Notes
    -----
    Common models:
    - gpt-4o: Most capable, expensive
    - gpt-4o-mini: Balanced performance/cost
    - gpt-3.5-turbo: Fastest, cheapest
    """
    import config.settings as settings
    settings.LLM_MODEL = model_name
    print(f"✅ LLM model set to: {model_name}")


def set_vision_model(model_name: str) -> None:
    """
    Set the vision model for image analysis.
    
    Parameters
    ----------
    model_name : str
        OpenAI vision model name (e.g., 'gpt-4o', 'gpt-4o-mini')
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> aba.set_vision_model("gpt-4o")
    ✅ Vision model set to: gpt-4o
    
    Notes
    -----
    Vision-capable models:
    - gpt-4o: Best vision understanding
    - gpt-4o-mini: Good balance for most tasks
    """
    import config.settings as settings
    settings.VISION_LLM_MODEL = model_name
    print(f"✅ Vision model set to: {model_name}")


def set_embed_model(model_name: str) -> None:
    """
    Set the embedding model for vector database.
    
    Parameters
    ----------
    model_name : str
        OpenAI embedding model name
        (e.g., 'text-embedding-3-large', 'text-embedding-3-small', 'text-embedding-ada-002')
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> aba.set_embed_model("text-embedding-3-large")
    ✅ Embedding model set to: text-embedding-3-large
    ⚠️  Note: Changing embedding model requires rebuilding vector databases!
    
    Notes
    -----
    Available embedding models:
    - text-embedding-3-large: 3072 dimensions, best quality
    - text-embedding-3-small: 1536 dimensions, balanced (default)
    - text-embedding-ada-002: 1536 dimensions, legacy model
    
    WARNING: If you change the embedding model, you must rebuild all
    vector databases using add_papers() and add_urls() with the new model.
    Existing databases will be incompatible!
    """
    import config.settings as settings
    settings.EMBED_MODEL = model_name
    print(f"✅ Embedding model set to: {model_name}")
    print("⚠️  Note: Changing embedding model requires rebuilding vector databases!")


def get_models() -> dict:
    """
    Get currently configured models.
    
    Returns
    -------
    dict
        Dictionary with 'llm', 'vision', and 'embed' model names
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> models = aba.get_models()
    >>> print(f"LLM: {models['llm']}")
    >>> print(f"Vision: {models['vision']}")
    >>> print(f"Embedding: {models['embed']}")
    """
    from config.settings import LLM_MODEL, VISION_LLM_MODEL, EMBED_MODEL
    
    return {
        "llm": LLM_MODEL,
        "vision": VISION_LLM_MODEL,
        "embed": EMBED_MODEL
    }


# ============================================================================
# 3. Knowledge Base Management - PDF Papers
# ============================================================================

def add_papers(
    pdf_path: Union[str, Path],
    collection: str = "papers",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    verbose: bool = True
) -> None:
    """
    Add PDF papers to a knowledge base collection.
    
    This function builds a vector database from research papers for RAG retrieval.
    Use this for your scientific literature, research papers, and publications.
    
    This function:
    1. Loads PDF(s) from a file or folder
    2. Splits them into chunks
    3. Embeds them using OpenAI embeddings
    4. Stores them in a Chroma vector database
    
    Parameters
    ----------
    pdf_path : str or Path
        Path to a PDF file OR folder containing PDF files
    collection : str, default="papers"
        Name of the collection (use descriptive names like "microscopy_papers", 
        "crispr_papers", "segmentation_papers", etc.)
    chunk_size : int, default=1000
        Size of text chunks for embedding
    chunk_overlap : int, default=200
        Overlap between chunks for context
    verbose : bool, default=True
        Print progress information
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # Add a single PDF paper
    >>> aba.add_papers("paper.pdf", collection="important_paper")
    >>> 
    >>> # Add all papers from a folder
    >>> aba.add_papers("papers/microscopy", collection="microscopy_papers")
    >>> 
    >>> # Build topic-specific collections
    >>> aba.add_papers("papers/segmentation", collection="segmentation_papers")
    >>> aba.add_papers("papers/crispr", collection="crispr_papers")
    >>> 
    >>> # Add with custom chunk settings
    >>> aba.add_papers("papers/general", collection="general_papers", 
    ...               chunk_size=500, chunk_overlap=100)
    
    Notes
    -----
    - Use descriptive collection names to organize your literature
    - Papers are for scientific literature, NOT for code documentation
    - For code/API documentation, use add_urls() instead
    - **Important**: This function APPENDS to existing collections
    - To replace a collection, delete it first: delete_collection(name)
    
    Examples of updating vs replacing:
    >>> # Append new papers to existing collection
    >>> aba.add_papers("new_papers/", collection="my_papers")  # Adds to existing
    >>> 
    >>> # Replace entire collection
    >>> aba.delete_collection("my_papers", confirm=False)  # Delete old
    >>> aba.add_papers("papers/", collection="my_papers")  # Create fresh
    """
    from data.document_loader import load_pdfs_from_folder, clean_text
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from core.embeddings import get_embeddings
    from config.settings import CHROMA_DIR
    from tqdm import tqdm
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Path not found: {pdf_path}")
    
    # Check if it's a file or folder
    if pdf_path.is_file():
        # Single PDF file
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF, got: {pdf_path.suffix}")
        
        if verbose:
            print(f"\n📄 Adding single paper: {pdf_path.name}")
            print(f"📊 Collection: {collection}\n")
        
        # Load single PDF
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = pdf_path.name
            if verbose:
                print(f"✅ Loaded {len(docs)} pages from {pdf_path.name}")
        except Exception as e:
            raise ValueError(f"Error loading PDF: {e}")
    
    elif pdf_path.is_dir():
        # Folder of PDFs
        if verbose:
            print(f"\n📚 Adding papers from folder: {pdf_path}")
            print(f"📊 Collection: {collection}\n")
        
        # Load all PDFs from folder
        docs = load_pdfs_from_folder(str(pdf_path))
    
    else:
        raise ValueError(f"Path must be a file or directory: {pdf_path}")
    
    if not docs:
        raise ValueError(f"No PDFs found or loaded from {pdf_path}")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = splitter.split_documents(docs)
    
    if verbose:
        print(f"✂️  Split into {len(split_docs)} chunks")
    
    # Clean text
    if verbose:
        print("🧹 Cleaning text...")
    
    cleaned_docs = []
    iterator = tqdm(split_docs, desc="Cleaning") if verbose else split_docs
    for d in iterator:
        try:
            d.page_content = clean_text(d.page_content)
            cleaned_docs.append(d)
        except Exception as e:
            if verbose:
                print(f"⚠️  Skipped chunk: {e}")
    
    # Embed and store
    if verbose:
        print(f"🔮 Creating embeddings and storing in ChromaDB...")
    
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        cleaned_docs,
        embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=collection
    )
    vectordb.persist()
    
    if verbose:
        print(f"✅ Successfully added {len(cleaned_docs)} chunks to '{collection}'")
        print(f"💾 Database location: {CHROMA_DIR}\n")


# ============================================================================
# 4. Knowledge Base Management - Web URLs (Code/Documentation)
# ============================================================================

def add_urls(
    urls: Union[str, List[str]],
    collection: str = "code_docs",
    max_depth: int = 1,
    max_pages: int = 100,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    verbose: bool = True
) -> None:
    """
    Add web documentation by scraping URLs.
    
    This function builds a vector database from online documentation, tutorials,
    and API references. Use this for code documentation, technical guides, and 
    online resources (NOT for research papers - use add_papers() for that).
    
    Default URLs are included in the code for common imaging libraries:
    - ImageJ/Fiji documentation
    - scikit-image documentation
    - OpenCV documentation
    - Pillow documentation
    - LangChain API reference
    
    This function:
    1. Scrapes content from the provided URLs
    2. Optionally crawls linked pages (controlled by max_depth)
    3. Splits content into chunks
    4. Embeds and stores in vector database
    
    Parameters
    ----------
    urls : str or list of str
        Single URL or list of URLs to scrape (adds to default URLs)
    collection : str, default="code_docs"
        Name of the collection (use descriptive names like "opencv_docs",
        "napari_docs", "custom_tool_docs", etc.)
    max_depth : int, default=1
        How many levels deep to crawl (1 = only provided URLs)
    max_pages : int, default=100
        Maximum number of pages to scrape per root URL
    chunk_size : int, default=1000
        Size of text chunks for embedding
    chunk_overlap : int, default=200
        Overlap between chunks
    verbose : bool, default=True
        Print progress information
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # Add single URL to default collection
    >>> aba.add_urls("https://napari.org/stable/")
    >>> 
    >>> # Add multiple URLs with custom collection name
    >>> urls = [
    ...     "https://scikit-image.org/docs/stable/",
    ...     "https://docs.opencv.org/4.x/",
    ...     "https://pillow.readthedocs.io/"
    ... ]
    >>> aba.add_urls(urls, collection="image_processing_docs")
    >>> 
    >>> # Add tool-specific documentation
    >>> aba.add_urls("https://cellprofiler.org/", collection="cellprofiler_docs")
    >>> 
    >>> # Add with deep crawling for comprehensive coverage
    >>> aba.add_urls("https://docs.example.com", 
    ...              collection="my_tool_docs",
    ...              max_depth=2, max_pages=200)
    
    Notes
    -----
    - URLs are for code documentation and tutorials, NOT research papers
    - For research papers (PDFs), use add_papers() instead
    - Default imaging library docs are already included in code
    - Use descriptive collection names to organize different tools
    - **Important**: This function APPENDS to existing collections
    - To replace a collection, delete it first: delete_collection(name)
    
    Examples of updating vs replacing:
    >>> # Append new URLs to existing collection
    >>> aba.add_urls(["https://new-docs.com"], collection="my_docs")  # Adds to existing
    >>> 
    >>> # Replace entire collection
    >>> aba.delete_collection("my_docs", confirm=False)  # Delete old
    >>> aba.add_urls(urls, collection="my_docs")  # Create fresh
    """
    from data.fiji_scraper import scrape_and_build_db
    
    if isinstance(urls, str):
        urls = [urls]
    
    if verbose:
        print(f"\n🌐 Adding web documentation from {len(urls)} URL(s)")
        print(f"📊 Collection: {collection}\n")
    
    scrape_and_build_db(
        root_urls=urls,
        collection_name=collection,
        max_links_per_root=max_pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        verbose=verbose
    )
    
    if verbose:
        print(f"✅ Successfully added web docs to '{collection}'\n")


# ============================================================================
# 5. Query Interface
# ============================================================================

def ask(
    question: str,
    image_path: Optional[str] = None,
    pdf_path: Optional[str] = None,
    stream: bool = False
) -> Union[str, List[str]]:
    """
    Ask the AI agent a question.
    
    The router automatically selects the right agent based on:
    - Paper review keywords → Paper Reviewer Agent
    - Image-related keywords + image file → Image Analyst Agent
    - General questions → AI Scientist Agent (with RAG)
    
    Parameters
    ----------
    question : str
        Your question or request
    image_path : str, optional
        Path to an image file for analysis
    pdf_path : str, optional
        Path to a PDF file for review
    stream : bool, default=False
        If True, returns generator for streaming responses
    
    Returns
    -------
    str or generator
        Agent's response (string) or response stream (generator)
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # Ask about literature
    >>> response = aba.ask("What is adaptive optics in microscopy?")
    >>> print(response)
    >>> 
    >>> # Analyze an image
    >>> response = aba.ask(
    ...     "What segmentation method should I use?",
    ...     image_path="microscopy_image.tif"
    ... )
    >>> 
    >>> # Review a paper
    >>> response = aba.ask(
    ...     "Summarize this paper's methodology",
    ...     pdf_path="research_paper.pdf"
    ... )
    >>> 
    >>> # Streaming response
    >>> for chunk in aba.ask("Explain CRISPR", stream=True):
    ...     print(chunk, end="", flush=True)
    """
    from core.router import Router
    
    router = Router()
    
    if stream:
        return router.route_query_stream(
            query=question,
            image_path=image_path,
            pdf_path=pdf_path
        )
    else:
        return router.route_query(
            query=question,
            image_path=image_path,
            pdf_path=pdf_path
        )


def chat(mode: str = "cli") -> None:
    """
    Start an interactive chat session.
    
    Parameters
    ----------
    mode : str, default="cli"
        Chat mode: "cli" for terminal or "gradio" for web UI
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # Terminal chat
    >>> aba.chat()
    >>> 
    >>> # Web UI chat
    >>> aba.chat(mode="gradio")
    """
    if mode == "cli":
        _run_cli()
    elif mode == "gradio":
        _run_gradio()
    else:
        raise ValueError(f"Invalid mode: {mode}. Choose 'cli' or 'gradio'.")


def _run_cli():
    """
    Simple command-line chat loop for testing routing logic.
    """
    from core.router import Router
    
    router = Router()
    print("🧠 AI Scientist CLI Mode")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            query = input("💬 Enter your query: ").strip()
            if query.lower() in ["exit", "quit"]:
                break

            img_path = input("🖼️ Optional image path (press Enter to skip): ").strip() or None
            pdf_path = input("📄 Optional PDF path (press Enter to skip): ").strip() or None

            response, label = router.route_query(
                query=query,
                session_id="cli_session",
                image_path=img_path,
                pdf_path=pdf_path,
            )
            print(f"\n➡ Routed to [{label.upper()}]\n")
            print(f"🧩 Response:\n{response}\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting gracefully...")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}\n")


def _run_gradio():
    """
    Launch the Gradio web interface.
    """
    import sys
    try:
        from ui.app_gradio import build_interface
    except ImportError as e:
        print(f"❌ Failed to import Gradio app: {e}")
        print("💡 Make sure gradio and Pillow are installed: pip install gradio Pillow")
        sys.exit(1)

    demo = build_interface()
    demo.queue(status_update_rate=0.1).launch(debug=True)


# ============================================================================
# 6. Database Management
# ============================================================================

def list_collections() -> List[str]:
    """
    List all available knowledge base collections.
    
    Shows both paper collections and code documentation collections.
    
    Returns
    -------
    list of str
        Names of all collections in the database
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> collections = aba.list_collections()
    >>> print(f"Available collections: {collections}")
    ['papers', 'code_docs', 'microscopy_papers', 'opencv_docs']
    
    Notes
    -----
    Collections are organized by purpose:
    - Papers: Research papers and publications (from add_papers())
    - Docs: Code documentation and tutorials (from add_urls())
    """
    from chromadb import PersistentClient
    from config.settings import CHROMA_DIR
    
    client = PersistentClient(path=CHROMA_DIR)
    collections = client.list_collections()
    
    collection_names = [c.name for c in collections]
    
    print(f"\n📚 Available collections ({len(collection_names)}):")
    for name in collection_names:
        print(f"  • {name}")
    print()
    
    return collection_names


def search_collection(
    query: str,
    collection: str = "bioimage_segmentation",
    top_k: int = 5
) -> List[dict]:
    """
    Search within a specific knowledge base collection.
    
    Parameters
    ----------
    query : str
        Search query
    collection : str, default="bioimage_segmentation"
        Collection name to search in
    top_k : int, default=5
        Number of top results to return
    
    Returns
    -------
    list of dict
        Search results with 'content', 'source', and 'score' keys
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> results = aba.search_collection(
    ...     "cell segmentation methods",
    ...     collection="bioimage_segmentation",
    ...     top_k=3
    ... )
    >>> 
    >>> for i, result in enumerate(results, 1):
    ...     print(f"{i}. {result['source']} (score: {result['score']:.3f})")
    ...     print(f"   {result['content'][:200]}...")
    """
    from langchain_community.vectorstores import Chroma
    from core.embeddings import get_embeddings
    from config.settings import CHROMA_DIR
    
    vectorstore = Chroma(
        collection_name=collection,
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings()
    )
    
    results = vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
    
    formatted_results = []
    print(f"\n🔍 Search results for: '{query}' in '{collection}':\n")
    
    for i, (doc, score) in enumerate(results, 1):
        result = {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": score
        }
        formatted_results.append(result)
        
        snippet = doc.page_content[:150].replace("\n", " ")
        print(f"{i}. {result['source']} (relevance: {score:.3f})")
        print(f"   {snippet}...\n")
    
    return formatted_results


def delete_collection(collection: str, confirm: bool = False) -> None:
    """
    Delete a knowledge base collection.
    
    Parameters
    ----------
    collection : str
        Name of collection to delete
    confirm : bool, default=False
        Must be True to actually delete (safety measure)
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # This will show a warning
    >>> aba.delete_collection("old_collection")
    ⚠️  Safety check: set confirm=True to actually delete
    >>> 
    >>> # This will delete
    >>> aba.delete_collection("old_collection", confirm=True)
    ✅ Deleted collection 'old_collection'
    """
    if not confirm:
        print("⚠️  Safety check: set confirm=True to actually delete")
        print(f"   Example: delete_collection('{collection}', confirm=True)")
        return
    
    from chromadb import PersistentClient
    from config.settings import CHROMA_DIR
    
    client = PersistentClient(path=CHROMA_DIR)
    
    try:
        client.delete_collection(collection)
        print(f"✅ Deleted collection '{collection}'")
    except Exception as e:
        print(f"❌ Error deleting collection: {e}")


# ============================================================================
# 7. Agent Direct Access (Advanced)
# ============================================================================

def get_scientist_agent():
    """Get AI Scientist Agent for custom workflows."""
    from agents.AI_scientist_agent import AIScientistAgent
    return AIScientistAgent()


def get_image_analyst():
    """Get Image Analyst Agent for custom workflows."""
    from agents.Image_analyst_agent import ImageAnalystAgent
    return ImageAnalystAgent()


def get_paper_reviewer():
    """Get Paper Reviewer Agent for custom workflows."""
    from agents.paper_reviewer_agent import PaperReviewerAgent
    return PaperReviewerAgent()


def get_router():
    """Get Router for custom workflows."""
    from core.router import Router
    return Router()


# ============================================================================
# 8. Utility Functions
# ============================================================================

def info() -> dict:
    """
    Get package information and configuration.
    
    Returns
    -------
    dict
        Package information including version, database location, models, etc.
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> info = aba.info()
    >>> print(f"Database: {info['database_path']}")
    >>> print(f"LLM: {info['llm_model']}")
    >>> print(f"Embedding: {info['embed_model']}")
    """
    from config.settings import CHROMA_DIR, LLM_MODEL, VISION_LLM_MODEL, EMBED_MODEL
    
    info_dict = {
        "version": __version__,
        "database_path": CHROMA_DIR,
        "llm_model": LLM_MODEL,
        "vision_model": VISION_LLM_MODEL,
        "embed_model": EMBED_MODEL,
        "api_key_set": bool(get_api_key())
    }
    
    print("\n" + "="*60)
    print("AI Bio Agent - Package Information")
    print("="*60)
    print(f"{'version':<20s}: {info_dict['version']}")
    print(f"{'database_path':<20s}: {info_dict['database_path']}")
    print(f"{'llm_model':<20s}: {info_dict['llm_model']}")
    print(f"{'vision_model':<20s}: {info_dict['vision_model']}")
    print(f"{'embed_model':<20s}: {info_dict['embed_model']}")
    print(f"{'api_key_set':<20s}: {info_dict['api_key_set']}")
    print("="*60 + "\n")
    
    return info_dict


def get_default_urls() -> List[str]:
    """
    Get the list of default URLs included for code documentation.
    
    These URLs are automatically available and include documentation for:
    - ImageJ/Fiji
    - scikit-image
    - OpenCV
    - Pillow
    - LangChain
    
    Returns
    -------
    list of str
        List of default documentation URLs
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> urls = aba.get_default_urls()
    >>> print(f"Default URLs: {len(urls)} documentation sites")
    >>> for url in urls:
    ...     print(f"  - {url}")
    
    Notes
    -----
    These URLs are used when building the default code documentation database.
    You can add more URLs using add_urls() to extend the knowledge base.
    """
    from data.fiji_scraper import TECH_ROOT_URLS
    
    print("\n" + "="*60)
    print("Default Code Documentation URLs")
    print("="*60)
    print(f"\n📚 {len(TECH_ROOT_URLS)} default documentation sources:\n")
    
    for i, url in enumerate(TECH_ROOT_URLS, 1):
        print(f"{i:2d}. {url}")
    
    print("\n" + "="*60)
    print("💡 Add more with: aba.add_urls(['your-url'], collection='name')")
    print("="*60 + "\n")
    
    return TECH_ROOT_URLS


# ============================================================================
# 9. Quick Setup Helper
# ============================================================================

def quickstart(api_key: str, pdf_folder: Optional[str] = None) -> None:
    """
    Quick setup for first-time users.
    
    This function:
    1. Sets up your API key
    2. Optionally adds papers from a folder
    3. Lists available collections
    
    Parameters
    ----------
    api_key : str
        Your OpenAI API key
    pdf_folder : str, optional
        Path to folder with PDF papers
    
    Examples
    --------
    >>> import aibioagent as aba
    >>> 
    >>> # Minimal setup
    >>> aba.quickstart("sk-your-key-here")
    >>> 
    >>> # Setup with papers
    >>> aba.quickstart("sk-your-key-here", pdf_folder="papers/")
    """
    print("\n" + "="*60)
    print("🚀 AI Bio Agent - Quick Start")
    print("="*60 + "\n")
    
    # Step 1: API Key
    print("Step 1: Setting up API key...")
    set_api_key(api_key, save_to_env=True)
    
    # Step 2: Add papers if provided
    if pdf_folder:
        print("\nStep 2: Adding papers to knowledge base...")
        add_papers(pdf_folder)
    else:
        print("\nStep 2: Skipped (no pdf_folder provided)")
        print("  💡 Tip: Add papers later with aba.add_papers('folder_path')")
    
    # Step 3: Show collections
    print("\nStep 3: Available collections:")
    list_collections()
    
    print("="*60)
    print("✅ Setup complete! You can now use:")
    print("   • aba.ask('your question')")
    print("   • aba.chat()  # Start interactive chat")
    print("   • aba.add_urls(['url'])  # Add web docs")
    print("="*60 + "\n")


# ============================================================================
# Export all public functions
# ============================================================================

__all__ = [
    # API Key
    "set_api_key",
    "get_api_key",
    # Knowledge Base - Papers
    "add_papers",
    # Knowledge Base - URLs
    "add_urls",
    "get_default_urls",
    # Query
    "ask",
    "chat",
    # Database Management
    "list_collections",
    "search_collection",
    "delete_collection",
    # Direct Agent Access
    "get_scientist_agent",
    "get_image_analyst",
    "get_paper_reviewer",
    "get_router",
    # Utilities
    "info",
    "quickstart",
]


# ============================================================================
# Module-level docstring for help()
# ============================================================================

__version__ = "0.3.2"
__author__ = "Chen Li"

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("Available functions:")
    print("="*60)
    for func_name in __all__:
        print(f"  • {func_name}")
    print("="*60)
    print("\nFor detailed help: help(aibioagent.function_name)")
