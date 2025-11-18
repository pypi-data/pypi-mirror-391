"""
core/smart_retriever.py
-----------------------
Smart retrieval system that automatically finds and searches the right collections.

This solves the problem of hardcoded collection names in agents.
"""

from typing import List, Dict, Any
from chromadb import PersistentClient
from langchain_community.vectorstores import Chroma
from core.embeddings import get_embeddings
from config.settings import CHROMA_DIR


class SmartRetriever:
    """
    Smart retriever that automatically searches across relevant collections.
    
    This class:
    1. Auto-detects available collections
    2. Categorizes them (papers vs code docs)
    3. Searches the appropriate ones based on query context
    """
    
    def __init__(self):
        """Initialize smart retriever with collection detection."""
        self.embeddings = get_embeddings()
        self.client = PersistentClient(path=CHROMA_DIR)
        self._refresh_collections()
    
    def _refresh_collections(self):
        """Detect and categorize all available collections."""
        all_collections = self.client.list_collections()
        
        self.paper_collections = []
        self.code_collections = []
        self.all_collection_names = []
        
        for collection in all_collections:
            name = collection.name
            self.all_collection_names.append(name)
            
            # Categorize based on name patterns
            if any(keyword in name.lower() for keyword in ['paper', 'publication', 'research', 'microscopy', 'crispr', 'segmentation']):
                self.paper_collections.append(name)
            elif any(keyword in name.lower() for keyword in ['doc', 'code', 'tech', 'api', 'tutorial', 'opencv', 'napari', 'fiji', 'imagej']):
                self.code_collections.append(name)
            else:
                # If unclear, add to both (safe default)
                self.paper_collections.append(name)
                self.code_collections.append(name)
    
    def get_available_collections(self) -> Dict[str, List[str]]:
        """
        Get categorized list of available collections.
        
        Returns
        -------
        dict
            Dictionary with 'papers', 'code', and 'all' keys
        """
        self._refresh_collections()
        return {
            'papers': self.paper_collections,
            'code': self.code_collections,
            'all': self.all_collection_names
        }
    
    def search_papers(self, query: str, k: int = 3) -> List[Any]:
        """
        Search across all paper collections.
        
        Parameters
        ----------
        query : str
            Search query
        k : int
            Number of results per collection
        
        Returns
        -------
        list
            Combined search results from all paper collections
        """
        self._refresh_collections()
        
        if not self.paper_collections:
            print("⚠️  No paper collections found. Add papers with aba.add_papers()")
            return []
        
        all_results = []
        for collection_name in self.paper_collections:
            try:
                vectorstore = Chroma(
                    collection_name=collection_name,
                    persist_directory=CHROMA_DIR,
                    embedding_function=self.embeddings
                )
                results = vectorstore.similarity_search(query, k=k)
                all_results.extend(results)
            except Exception as e:
                print(f"⚠️  Error searching {collection_name}: {e}")
        
        return all_results
    
    def search_code_docs(self, query: str, k: int = 3) -> List[Any]:
        """
        Search across all code documentation collections.
        
        Parameters
        ----------
        query : str
            Search query
        k : int
            Number of results per collection
        
        Returns
        -------
        list
            Combined search results from all code collections
        """
        self._refresh_collections()
        
        if not self.code_collections:
            print("⚠️  No code documentation collections found. Add with aba.add_urls()")
            return []
        
        all_results = []
        for collection_name in self.code_collections:
            try:
                vectorstore = Chroma(
                    collection_name=collection_name,
                    persist_directory=CHROMA_DIR,
                    embedding_function=self.embeddings
                )
                results = vectorstore.similarity_search(query, k=k)
                all_results.extend(results)
            except Exception as e:
                print(f"⚠️  Error searching {collection_name}: {e}")
        
        return all_results
    
    def search_all(self, query: str, k: int = 3) -> List[Any]:
        """
        Search across ALL collections.
        
        Parameters
        ----------
        query : str
            Search query
        k : int
            Number of results per collection
        
        Returns
        -------
        list
            Combined search results from all collections
        """
        self._refresh_collections()
        
        if not self.all_collection_names:
            print("⚠️  No collections found. Build databases with aba.add_papers() or aba.add_urls()")
            return []
        
        all_results = []
        for collection_name in self.all_collection_names:
            try:
                vectorstore = Chroma(
                    collection_name=collection_name,
                    persist_directory=CHROMA_DIR,
                    embedding_function=self.embeddings
                )
                results = vectorstore.similarity_search(query, k=k)
                all_results.extend(results)
            except Exception as e:
                print(f"⚠️  Error searching {collection_name}: {e}")
        
        return all_results
    
    def get_retriever(self, collection_type: str = "all", k: int = 3):
        """
        Get a retriever function for use in LangChain chains.
        
        Parameters
        ----------
        collection_type : str
            Type of collections to search: "papers", "code", or "all"
        k : int
            Number of results per collection
        
        Returns
        -------
        callable
            Retriever function compatible with LangChain
        """
        if collection_type == "papers":
            return lambda query: self.search_papers(query, k=k)
        elif collection_type == "code":
            return lambda query: self.search_code_docs(query, k=k)
        else:
            return lambda query: self.search_all(query, k=k)


# Singleton instance
_smart_retriever = None

def get_smart_retriever() -> SmartRetriever:
    """Get or create the global smart retriever instance."""
    global _smart_retriever
    if _smart_retriever is None:
        _smart_retriever = SmartRetriever()
    return _smart_retriever


if __name__ == "__main__":
    # Test smart retriever
    retriever = get_smart_retriever()
    collections = retriever.get_available_collections()
    
    print("\n" + "="*60)
    print("Smart Retriever - Available Collections")
    print("="*60)
    print(f"\n📄 Paper Collections ({len(collections['papers'])}):")
    for name in collections['papers']:
        print(f"  • {name}")
    
    print(f"\n💻 Code Documentation Collections ({len(collections['code'])}):")
    for name in collections['code']:
        print(f"  • {name}")
    
    print("\n" + "="*60)
