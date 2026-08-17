"""
RAG Service - Wraps existing retrieval, generation, and evaluation modules.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path to import existing modules
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import retrieval
import generation
import evaluation
from config import FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, BM25_INDEX_PATH


class RAGService:
    """Service wrapper for the RAG pipeline."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure indexes are loaded once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._index_loaded = False
        self._chunk_count = 0
        self._index_signature = None

    @staticmethod
    def _current_index_signature():
        """Identify the exact on-disk index version without reading its contents."""
        paths = (FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, BM25_INDEX_PATH)
        if not all(path.exists() for path in paths):
            return None
        return tuple((path.stat().st_mtime_ns, path.stat().st_size) for path in paths)
    
    def ensure_index_loaded(self) -> bool:
        """Ensure the index is loaded and return status."""
        signature = self._current_index_signature()
        if self._index_loaded and signature == self._index_signature:
            return True
        try:
            # A completed rebuild replaces these files atomically. Reload them
            # on the next request so every answer uses the latest corpus.
            retrieval.clear_caches()
            # Trigger index loading by getting index and metadata
            index, metadata = retrieval._get_index_and_metadata()
            self._chunk_count = len(metadata)
            self._index_loaded = True
            self._index_signature = self._current_index_signature()
            return True
        except FileNotFoundError:
            self._index_loaded = False
            return False
    
    def get_chunk_count(self) -> int:
        """Get the number of chunks in the index."""
        if not self._index_loaded:
            self.ensure_index_loaded()
        return self._chunk_count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        mode: str = "hybrid",
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant passages.
        
        Args:
            query: Search query
            top_k: Number of results
            mode: Retrieval mode (dense, bm25, hybrid)
            source_filter: Optional source filter
        
        Returns:
            List of passage dictionaries
        """
        self.ensure_index_loaded()
        return retrieval.search(
            query=query,
            top_k=top_k,
            mode=mode,
            source_filter=source_filter
        )
    
    def generate_answer(
        self,
        question: str,
        top_k: int = 5,
        mode: str = "hybrid",
        source_filter: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile"
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question.
        
        Args:
            question: User question
            top_k: Number of passages to retrieve
            mode: Retrieval mode
            source_filter: Optional source filter
            model: Groq model to use
        
        Returns:
            Dictionary with answer, passages, usage, etc.
        """
        self.ensure_index_loaded()
        return generation.generate_answer(
            question=question,
            top_k=top_k,
            retrieval_mode=mode,
            source_filter=source_filter,
            model=model
        )
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        passages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate a generated answer.
        
        Args:
            question: Original question
            answer: Generated answer
            passages: Retrieved passages
        
        Returns:
            Evaluation results
        """
        return evaluation.evaluate_response(
            question=question,
            answer=answer,
            passages=passages
        )
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Get information about available source documents."""
        self.ensure_index_loaded()
        _, metadata = retrieval._get_index_and_metadata()
        
        # Aggregate by document
        doc_info: Dict[str, Dict[str, Any]] = {}
        for chunk in metadata:
            filename = chunk["doc_filename"]
            if filename not in doc_info:
                doc_info[filename] = {
                    "filename": filename,
                    "title": chunk["title"],
                    "source": chunk["source"],
                    "topic": chunk["topic"],
                    "chunk_count": 0
                }
            doc_info[filename]["chunk_count"] += 1
        
        return list(doc_info.values())


# Singleton instance
rag_service = RAGService()
