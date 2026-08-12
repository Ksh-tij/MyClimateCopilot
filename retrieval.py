"""
retrieval.py
Phase 2: Vector Search & Retrieval Engine.

Loads the FAISS index, BM25 index, and metadata store, encodes search queries
using sentence-transformers, retrieves Top-K relevant passage chunks via
dense (cosine similarity), keyword (BM25), or hybrid (Reciprocal Rank Fusion
of both) search, and returns formatted citations.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from config import (
    FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, BM25_INDEX_PATH, EMBEDDING_MODEL_NAME, RRF_K
)
import bm25_utils

_MODEL_CACHE: Optional[SentenceTransformer] = None
_INDEX_CACHE: Optional[faiss.Index] = None
_METADATA_CACHE: Optional[List[Dict[str, Any]]] = None
_BM25_CACHE: Optional[BM25Okapi] = None


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


def _get_bm25_index() -> BM25Okapi:
    global _BM25_CACHE

    if not BM25_INDEX_PATH.exists():
        raise FileNotFoundError(
            f"BM25 index not found at {BM25_INDEX_PATH}. Please run 'python main.py index' first."
        )

    if _BM25_CACHE is None:
        with open(BM25_INDEX_PATH, "rb") as f:
            _BM25_CACHE = pickle.load(f)

    return _BM25_CACHE


def _dense_rank(query_vec: np.ndarray, fetch_k: int, index: faiss.Index) -> List[int]:
    """Returns an ordered list of corpus indices (best first) from FAISS."""
    scores, indices = index.search(query_vec, fetch_k)
    return [int(idx) for idx in indices[0] if idx >= 0]


def _bm25_rank(tokenized_query: List[str], fetch_k: int, bm25: BM25Okapi) -> List[int]:
    """Returns an ordered list of corpus indices (best first) with score > 0."""
    if not tokenized_query:
        return []
    scores = bm25.get_scores(tokenized_query)
    order = np.argsort(scores)[::-1]
    ranked = [int(i) for i in order if scores[i] > 0]
    return ranked[:fetch_k]


def _reciprocal_rank_fusion(rank_lists: List[List[int]], k: int = RRF_K) -> Dict[int, float]:
    """Fuses multiple ranked lists of corpus indices into a single score per index."""
    fused: Dict[int, float] = {}
    for ranked in rank_lists:
        for pos, idx in enumerate(ranked):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + pos + 1)
    return fused


def _build_result(
    idx: int,
    metadata: List[Dict[str, Any]],
    score: float,
    mode: str,
    matched_by: Optional[List[str]] = None
) -> Dict[str, Any]:
    meta = metadata[idx]
    result = {
        "score": score,
        "mode": mode,
        "chunk_id": meta["chunk_id"],
        "doc_filename": meta["doc_filename"],
        "title": meta["title"],
        "source": meta["source"],
        "topic": meta["topic"],
        "page_number": meta["page_number"],
        "text": meta["text"]
    }
    if matched_by is not None:
        result["matched_by"] = matched_by
    return result


def search(
    query: str,
    top_k: int = 5,
    source_filter: Optional[str] = None,
    mode: str = "dense"
) -> List[Dict[str, Any]]:
    """
    Search for passages relevant to `query`.

    Args:
        query: natural language user query string
        top_k: number of top results to return
        source_filter: optional source name (e.g. "FAO", "IPCC") to filter results
        mode: "dense" (FAISS cosine similarity, default), "bm25" (keyword search),
              or "hybrid" (both, merged via Reciprocal Rank Fusion)

    Returns:
        List of dicts containing score, mode, chunk_id, title, source, topic,
        page_number, text (and matched_by for hybrid results)
    """
    if not query.strip():
        return []

    index, metadata = _get_index_and_metadata()

    if mode == "dense":
        model = _get_model()
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

            results.append(_build_result(int(idx), metadata, float(score), mode="dense"))

            if len(results) >= top_k:
                break

        return results

    if mode == "bm25":
        bm25 = _get_bm25_index()
        tokenized_query = bm25_utils.tokenize(query)

        base_pool = max(top_k * 4, 20)
        fetch_k = min(base_pool * 5 if source_filter else base_pool, len(metadata))

        bm25_scores = bm25.get_scores(tokenized_query) if tokenized_query else None
        ranked = _bm25_rank(tokenized_query, fetch_k, bm25)

        results = []
        for idx in ranked:
            meta = metadata[idx]
            if source_filter and meta.get("source", "").lower() != source_filter.lower():
                continue

            results.append(_build_result(idx, metadata, float(bm25_scores[idx]), mode="bm25"))

            if len(results) >= top_k:
                break

        return results

    if mode == "hybrid":
        model = _get_model()
        bm25 = _get_bm25_index()

        query_vec = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)
        tokenized_query = bm25_utils.tokenize(query)

        base_pool = max(top_k * 4, 20)
        fetch_k = min(base_pool * 5 if source_filter else base_pool, len(metadata))

        dense_ranked = _dense_rank(query_vec, fetch_k, index)
        bm25_ranked = _bm25_rank(tokenized_query, fetch_k, bm25)

        fused = _reciprocal_rank_fusion([dense_ranked, bm25_ranked])
        sorted_idx = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)

        dense_set, bm25_set = set(dense_ranked), set(bm25_ranked)
        results = []
        for idx in sorted_idx:
            meta = metadata[idx]
            if source_filter and meta.get("source", "").lower() != source_filter.lower():
                continue

            matched_by = [name for name, s in (("dense", dense_set), ("bm25", bm25_set)) if idx in s]
            results.append(_build_result(idx, metadata, fused[idx], mode="hybrid", matched_by=matched_by))

            if len(results) >= top_k:
                break

        return results

    raise ValueError(f"Unknown mode: {mode!r}. Expected 'dense', 'bm25', or 'hybrid'.")


def print_search_results(query: str, results: List[Dict[str, Any]], mode: str = "dense") -> None:
    """Pretty prints search results to the console."""
    print(f"\n==================================================")
    print(f" [SEARCH] Query: '{query}' (mode: {mode})")
    print(f" Found {len(results)} relevant passage(s)")
    print(f"==================================================\n")

    for i, res in enumerate(results, 1):
        res_mode = res.get("mode", mode)
        if res_mode == "dense":
            score_pct = round(res['score'] * 100, 1)
            score_line = f"Similarity Score: {res['score']:.4f} ({score_pct}%)"
        elif res_mode == "bm25":
            score_line = f"BM25 Score: {res['score']:.4f}"
        else:  # hybrid
            matched_by = ", ".join(res.get("matched_by", []))
            score_line = f"RRF Fused Score: {res['score']:.5f}  [matched_by: {matched_by}]"

        print(f"--- Result #{i} [{score_line}] ---")
        print(f"  Document: {res['title']} ({res['doc_filename']})")
        print(f"  Source:   {res['source']} | Topic: {res['topic']} | Page: {res['page_number']}")
        print(f"  Passage:\n{res['text']}\n")


if __name__ == "__main__":
    test_query = "What are the impacts of drought and climate change on crop yields?"
    res = search(test_query, top_k=3)
    print_search_results(test_query, res)
