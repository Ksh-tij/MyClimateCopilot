"""
config.py
Central configuration for the Climate CoPilot data pipeline.
Change paths/settings here — every other module imports from this file.
"""

from pathlib import Path

# ---- Project root & data folders ----
PROJECT_ROOT = Path(__file__).resolve().parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"           # original downloaded/collected PDFs land here
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"  # cleaned extracted text (per-document .json) lands here
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"        # passage chunks land here
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore" # FAISS index and metadata land here
LOG_DIR = PROJECT_ROOT / "logs"

METADATA_CSV = RAW_DIR / "metadata.csv"            # tracks every collected document (Week 1-2 deliverable)
PREPROCESS_LOG = LOG_DIR / "preprocessing_log.csv"  # tracks extraction results per document (Week 3 deliverable)
CHUNKS_JSON = CHUNKS_DIR / "chunks.json"           # passage chunks file
FAISS_INDEX_PATH = VECTORSTORE_DIR / "index.faiss" # FAISS index file
CHUNKS_METADATA_PATH = VECTORSTORE_DIR / "chunks_metadata.json" # metadata index for retrieval

# ---- Preprocessing settings ----
MIN_TEXT_LENGTH = 200          # documents that extract to fewer characters than this are flagged as "low_text"
                                # (usually means the PDF is scanned/image-based and needs OCR later)

# Header/footer cleanup: lines shorter than this that repeat across many pages are stripped
REPEATED_LINE_MAX_LEN = 80
REPEATED_LINE_MIN_PAGE_FRACTION = 0.4   # a short line appearing on >=40% of pages is treated as a header/footer

# ---- Chunking settings ----
CHUNK_SIZE = 600              # target character length per passage chunk (~100-120 words)
CHUNK_OVERLAP = 150           # overlap between consecutive chunks (~25-30 words)

# ---- Embedding Model settings ----
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Ensure folders exist whenever config is imported
for _dir in (RAW_DIR, PROCESSED_DIR, CHUNKS_DIR, VECTORSTORE_DIR, LOG_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
