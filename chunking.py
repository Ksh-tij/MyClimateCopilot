"""
chunking.py
Phase 2: Document Passage Chunking.

Reads cleaned page-level JSON files from data/processed/, splits text into
overlapping passages of configurable character length, and exports all chunks
with metadata to data/chunks/chunks.json.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any

from config import (
    PROCESSED_DIR, CHUNKS_JSON, METADATA_CSV, CHUNK_SIZE, CHUNK_OVERLAP
)


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Splits text into overlapping character passages, respecting word boundaries
    where possible to avoid splitting words in half.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:].strip())
            break

        # Adjust end to nearest whitespace boundary to avoid cutting words
        space_idx = text.rfind(" ", start, end)
        if space_idx > start:
            end = space_idx

        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append(chunk_str)

        # Move start forward by chunk_size - chunk_overlap
        next_start = end - chunk_overlap
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def create_chunks() -> List[Dict[str, Any]]:
    """
    Process all JSON files in PROCESSED_DIR and generate passage chunks.
    Saves and returns the complete list of chunk dictionaries.
    """
    # Read metadata.csv to only chunk curated documents
    if METADATA_CSV.exists():
        with open(METADATA_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Get valid stems from metadata.csv (first 18 entries or all metadata entries)
            allowed_stems = {Path(row["filename"]).stem for row in reader if row.get("filename")}
        processed_files = [f for f in sorted(PROCESSED_DIR.glob("*.json")) if f.stem in allowed_stems]
    else:
        processed_files = sorted(PROCESSED_DIR.glob("*.json"))

    if not processed_files:
        print(f"No matching processed JSON files found in {PROCESSED_DIR}. Run preprocessing first.")
        return []

    all_chunks = []
    chunk_counter = 0

    print(f"Chunking {len(processed_files)} curated document(s) (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")

    for file_path in processed_files:
        with open(file_path, "r", encoding="utf-8") as f:
            doc_data = json.load(f)

        doc_filename = doc_data.get("filename", file_path.name)
        title = doc_data.get("title", file_path.stem)
        source = doc_data.get("source", "Unknown")
        topic = doc_data.get("topic", "General")
        pages = doc_data.get("pages", [])

        doc_chunk_count = 0
        for page in pages:
            page_num = page.get("page_number", 1)
            page_text = page.get("text", "")
            if not page_text.strip():
                continue

            passages = _chunk_text(page_text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            for idx, passage in enumerate(passages):
                chunk_id = f"{file_path.stem}_p{page_num}_c{idx+1}"
                chunk_obj = {
                    "chunk_id": chunk_id,
                    "doc_filename": doc_filename,
                    "title": title,
                    "source": source,
                    "topic": topic,
                    "page_number": page_num,
                    "text": passage,
                    "char_count": len(passage)
                }
                all_chunks.append(chunk_obj)
                chunk_counter += 1
                doc_chunk_count += 1

        print(f"  [ok] {file_path.name} -> {doc_chunk_count} chunk(s)")

    # Save to data/chunks/chunks.json
    with open(CHUNKS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    avg_len = round(sum(c["char_count"] for c in all_chunks) / len(all_chunks), 1) if all_chunks else 0
    print(f"\nChunking complete!")
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Average chunk length: {avg_len} characters")
    print(f"Saved to: {CHUNKS_JSON}")

    return all_chunks


if __name__ == "__main__":
    create_chunks()
