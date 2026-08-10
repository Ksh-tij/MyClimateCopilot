"""
retrieval.py
Phase 2: Vector Search & Retrieval Engine.

Loads the FAISS index and metadata store, encodes search queries using
sentence-transformers, retrieves Top-K relevant passage chunks by cosine
similarity, and returns formatted citations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import (
    FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, EMBEDDING_MODEL_NAME
)

_MODEL_CACHE: Optional[SentenceTransformer] = None
_INDEX_CACHE: Optional[faiss.Index] = None
_METADATA_CACHE: Optional[List[Dict[str, Any]]] = None


def _get_model() -> SentenceTransformer:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _MODEL_CACHE


def _get_index_and_metadata() -> tuple[faiss.Index, List[Dict[str, Any]]]:
    global _INDEX_CACHE, _METADATA_CACHE

    if not FAISS_INDEX_PATH.exists() or not CHUNKS_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index or metadata map not found in {FAISS_INDEX_PATH.parent}. "
            "Please run 'python main.py index' first."
        )

    if _INDEX_CACHE is None:
        _INDEX_CACHE = faiss.read_index(str(FAISS_INDEX_PATH))

    if _METADATA_CACHE is None:
        with open(CHUNKS_METADATA_PATH, "r", encoding="utf-8") as f:
            _METADATA_CACHE = json.load(f)

    return _INDEX_CACHE, _METADATA_CACHE


def search(query: str, top_k: int = 5, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search the FAISS vector index for passages relevant to `query`.

    Args:
        query: natural language user query string
        top_k: number of top results to return
        source_filter: optional source name (e.g. "FAO", "IPCC") to filter results

    Returns:
        List of dicts containing score, chunk_id, title, source, topic, page_number, text
    """
    if not query.strip():
        return []

    index, metadata = _get_index_and_metadata()
    model = _get_model()

    # Encode query vector and normalize for cosine similarity
    query_vec = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype(np.float32)

    fetch_k = top_k * 5 if source_filter else top_k
    fetch_k = min(fetch_k, index.ntotal)

    scores, indices = index.search(query_vec, fetch_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        meta = metadata[idx]

        if source_filter and meta.get("source", "").lower() != source_filter.lower():
            continue

        results.append({
            "score": float(score),
            "chunk_id": meta["chunk_id"],
            "doc_filename": meta["doc_filename"],
            "title": meta["title"],
            "source": meta["source"],
            "topic": meta["topic"],
            "page_number": meta["page_number"],
            "text": meta["text"]
        })

        if len(results) >= top_k:
            break

    return results


def print_search_results(query: str, results: List[Dict[str, Any]]) -> None:
    """Pretty prints search results to the console."""
    print(f"\n==================================================")
    print(f" [SEARCH] Query: '{query}'")
    print(f" Found {len(results)} relevant passage(s)")
    print(f"==================================================\n")

    for i, res in enumerate(results, 1):
        score_pct = round(res['score'] * 100, 1)
        print(f"--- Result #{i} [Similarity Score: {res['score']:.4f} ({score_pct}%)] ---")
        print(f"  Document: {res['title']} ({res['doc_filename']})")
        print(f"  Source:   {res['source']} | Topic: {res['topic']} | Page: {res['page_number']}")
        print(f"  Passage:\n{res['text']}\n")


if __name__ == "__main__":
    test_query = "What are the impacts of drought and climate change on crop yields?"
    res = search(test_query, top_k=3)
    print_search_results(test_query, res)
