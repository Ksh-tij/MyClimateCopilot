"""
indexing.py
Phase 2: Embedding Generation and FAISS Vector Indexing.

Loads passage chunks from data/chunks/chunks.json, generates dense vector
embeddings using sentence-transformers (all-MiniLM-L6-v2), builds a FAISS IndexFlatIP
vector store (cosine similarity), and persists the index and metadata mapping.
"""

import json
import pickle
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from config import (
    CHUNKS_JSON, FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, BM25_INDEX_PATH, EMBEDDING_MODEL_NAME
)
import bm25_utils
import chunking


def build_index() -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    """
    Generate embeddings for all chunks and create/save the FAISS index and metadata.
    """
    if not CHUNKS_JSON.exists():
        print("chunks.json not found. Running chunking first...")
        chunks = chunking.create_chunks()
    else:
        with open(CHUNKS_JSON, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    if not chunks:
        raise ValueError("No chunks available to build index.")

    print(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    start_time = time.time()
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [c["text"] for c in chunks]
    print(f"Generating embeddings for {len(texts)} chunks...")
    
    # Encode with L2 normalization so Inner Product equals Cosine Similarity
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype(np.float32)

    dimension = embeddings.shape[1]
    print(f"Embeddings generated in {round(time.time() - start_time, 2)}s. Shape: {embeddings.shape}")

    # Build FAISS Index (IndexFlatIP for cosine similarity on normalized vectors)
    print(f"Building FAISS vector index (dimension={dimension})...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Persist FAISS index and metadata
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    # Strip text or keep text in metadata mapping for fast retrieval lookup
    metadata_list = []
    for idx, c in enumerate(chunks):
        metadata_list.append({
            "vector_id": idx,
            "chunk_id": c["chunk_id"],
            "doc_filename": c["doc_filename"],
            "title": c["title"],
            "source": c["source"],
            "topic": c["topic"],
            "page_number": c["page_number"],
            "text": c["text"]
        })

    with open(CHUNKS_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    # Build BM25 keyword index (aligned to the same chunk order as metadata_list,
    # so BM25 doc index i, FAISS vector_id i, and metadata[i] all refer to the same chunk)
    print("Building BM25 keyword index...")
    tokenized_corpus = [bm25_utils.tokenize(c["text"]) for c in chunks]
    bm25_index = BM25Okapi(tokenized_corpus)

    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(bm25_index, f)

    index_size_mb = round(FAISS_INDEX_PATH.stat().st_size / (1024 * 1024), 2)
    bm25_size_kb = round(BM25_INDEX_PATH.stat().st_size / 1024, 1)
    print(f"\nFAISS Index successfully built and saved!")
    print(f"Total vectors indexed: {index.ntotal}")
    print(f"Vector Dimension:     {dimension}")
    print(f"FAISS Index Path:     {FAISS_INDEX_PATH} ({index_size_mb} MB)")
    print(f"Metadata Map Path:    {CHUNKS_METADATA_PATH}")
    print(f"BM25 Index Path:      {BM25_INDEX_PATH} ({bm25_size_kb} KB)")

    return index, metadata_list


if __name__ == "__main__":
    build_index()
