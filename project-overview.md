# My Climate CoPilot

> **A Question Answering System for Climate Adaptation in Agriculture**

An LLM-powered retrieval-augmented generation (RAG) system designed to help climate experts, agronomists, and farmer advisors access relevant climate literature and data for agricultural adaptation decisions. This project implements the pipeline described in the ACL 2025 paper *"My Climate CoPilot: A Question Answering System for Climate Adaptation in Agriculture"*.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Data Flow Pipeline](#data-flow-pipeline)
- [Techniques & Methods](#techniques--methods)
- [Project Structure](#project-structure)
- [Implementation Status](#implementation-status)
- [Setup & Installation](#setup--installation)
- [Usage Guide](#usage-guide)
- [Roadmap](#roadmap)

---

## Overview

**My Climate CoPilot** addresses the challenge of finding relevant climate adaptation information from the ever-growing volume of climate literature and data. The system is designed to:

- **Answer climate adaptation questions** grounded in scientific literature
- **Retrieve relevant passages** from climate documents (IPCC, FAO, World Bank, etc.)
- **Support multiple retrieval modes**: Dense (semantic), BM25 (keyword), and Hybrid (fusion)
- **Provide transparent citations** linking answers to source documents

### Target Users
- 🌾 **Agronomists** seeking crop adaptation strategies
- 🌡️ **Climate scientists** researching regional impacts
- 🧑‍🌾 **Farmer advisors** providing climate-informed guidance

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MY CLIMATE COPILOT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐     │
│   │  DATA SOURCES    │    │  PREPROCESSING   │    │     INDEXING         │     │
│   │                  │    │                  │    │                      │     │
│   │  ┌────────────┐  │    │  ┌────────────┐  │    │  ┌────────────────┐  │     │
│   │  │ IPCC PDFs  │──┼───▶│  │ PyMuPDF    │  │    │  │ FAISS Vector   │  │     │
│   │  └────────────┘  │    │  │ Extraction │  │    │  │ Index (Dense)  │  │     │
│   │  ┌────────────┐  │    │  └──────┬─────┘  │    │  └────────┬───────┘  │     │
│   │  │  FAO PDFs  │──┼───▶│         ▼        │    │           │          │     │
│   │  └────────────┘  │    │  ┌────────────┐  │    │  ┌────────▼───────┐  │     │
│   │  ┌────────────┐  │    │  │ Text Clean │──┼───▶│  │ BM25 Inverted  │  │     │
│   │  │ World Bank │──┼───▶│  │ & Chunking │  │    │  │ Index (Sparse) │  │     │
│   │  └────────────┘  │    │  └────────────┘  │    │  └────────────────┘  │     │
│   └──────────────────┘    └──────────────────┘    └──────────────────────┘     │
│                                                              │                  │
│   ┌──────────────────────────────────────────────────────────▼─────────────┐   │
│   │                         RETRIEVAL ENGINE                                │   │
│   │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │  │  User Query ─▶ Encode (MiniLM-L6) ─▶ Search ─▶ Rank & Fuse (RRF) │   │   │
│   │  └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                         │   │
│   │  Retrieval Modes:                                                       │   │
│   │    • Dense: FAISS cosine similarity (semantic matching)                 │   │
│   │    • BM25:  Keyword-based ranking (term frequency)                      │   │
│   │    • Hybrid: Reciprocal Rank Fusion of both                             │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                      RESPONSE GENERATION (PLANNED)                       │   │
│   │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│   │  │  Retrieved Passages ─▶ LLM (Claude/GPT) ─▶ Generated Answer     │    │   │
│   │  │                        ─▶ Self-Evaluation ─▶ User Feedback      │    │   │
│   │  └─────────────────────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Pipeline

The system processes climate documents through a 5-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  STAGE 1                STAGE 2                STAGE 3                          │
│  ┌──────────┐          ┌──────────────┐       ┌────────────┐                   │
│  │ COLLECT  │          │ PREPROCESS   │       │  CHUNKING  │                   │
│  │          │          │              │       │            │                   │
│  │ PDFs ───▶│─────────▶│ Extract text │──────▶│ Split into │                   │
│  │ metadata │          │ Clean noise  │       │ passages   │                   │
│  │ hash     │          │ Remove hdrs  │       │ (512 chars)│                   │
│  └──────────┘          └──────────────┘       └────────────┘                   │
│       │                       │                      │                          │
│       ▼                       ▼                      ▼                          │
│  data/raw/             data/processed/         data/chunks/                     │
│  metadata.csv          *.json (per doc)        chunks.json                      │
│                                                                                 │
│  STAGE 4                STAGE 5                                                 │
│  ┌────────────────┐    ┌────────────────────────────────────────┐              │
│  │   INDEXING     │    │           RETRIEVAL / SEARCH           │              │
│  │                │    │                                        │              │
│  │ Generate       │    │  Query ──▶ Encode ──▶ Search Indices   │              │
│  │ embeddings     │───▶│                           │            │              │
│  │ Build FAISS    │    │           ┌───────────────┴──────────┐ │              │
│  │ Build BM25     │    │           ▼               ▼          │ │              │
│  │                │    │       FAISS            BM25          │ │              │
│  └────────────────┘    │       Results          Results       │ │              │
│       │                │           └───────────┬──────────────┘ │              │
│       ▼                │                       ▼                │              │
│  data/vectorstore/     │              RRF Fusion (Hybrid)       │              │
│  index.faiss           │                       │                │              │
│  bm25_index.pkl        │                       ▼                │              │
│  chunks_metadata.json  │           Top-K Ranked Passages        │              │
│                        └────────────────────────────────────────┘              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Details

| Stage | Input | Process | Output |
|-------|-------|---------|--------|
| **1. Collection** | PDF files | Hash, copy, log metadata | `data/raw/*.pdf`, `metadata.csv` |
| **2. Preprocessing** | Raw PDFs | PyMuPDF extraction, header removal, text cleaning | `data/processed/*.json` |
| **3. Chunking** | Cleaned JSON | Split into 512-char overlapping passages (100-char overlap) | `data/chunks/chunks.json` |
| **4. Indexing** | Chunks | Embed with MiniLM-L6, build FAISS + BM25 indices | `data/vectorstore/` |
| **5. Retrieval** | User query | Encode query, search indices, fuse results | Ranked passages |

---

## Techniques & Methods

### 1. Text Extraction & Cleaning
- **PyMuPDF (fitz)**: Page-by-page text extraction from PDFs
- **Header/Footer Detection**: Identifies repeated short lines across pages (appears on >40% of pages)
- **Noise Removal**: Strips page numbers, collapses whitespace, rejoins hyphenated words

### 2. Document Chunking
- **Fixed-size chunking**: 512 characters per chunk (configurable)
- **Overlapping windows**: 100-character overlap to preserve context across boundaries
- **Word-boundary aware**: Chunks break at whitespace to avoid splitting words

### 3. Embedding Generation
- **Model**: `all-MiniLM-L6-v2` from sentence-transformers
- **Dimension**: 384-dimensional dense vectors
- **Normalization**: L2-normalized for cosine similarity via inner product

### 4. Vector Indexing (FAISS)
- **Index Type**: `IndexFlatIP` (Inner Product on normalized vectors = Cosine Similarity)
- **No approximation**: Exact nearest-neighbor search for maximum accuracy

### 5. Keyword Indexing (BM25)
- **Algorithm**: BM25Okapi from `rank_bm25`
- **Tokenization**: Lowercase + alphanumeric word split
- **Aligned indexing**: BM25 doc indices match FAISS vector indices for easy fusion

### 6. Hybrid Retrieval (Reciprocal Rank Fusion)
- **Dense retrieval**: FAISS cosine similarity search
- **Sparse retrieval**: BM25 keyword matching
- **Fusion method**: RRF score = Σ 1/(k + rank), where k=60 (default)
- **Result**: Combines semantic understanding with keyword precision

---

## Project Structure

```
MyClimateCopilot/
│
├── main.py                 # CLI entry point (collect, preprocess, chunk, index, search, ask)
├── config.py               # Paths & configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # Quick start guide
├── project-overview.md     # This comprehensive documentation
├── .env                    # API keys (not in git)
├── .env.example            # Example environment file
├── .gitignore              # Git ignore patterns
│
├── data_collection.py      # Stage 1: PDF registration & metadata logging
├── preprocessing.py        # Stage 2: Text extraction & cleaning
├── chunking.py             # Stage 3: Passage splitting with overlap
├── indexing.py             # Stage 4: FAISS + BM25 index building
├── retrieval.py            # Stage 5: Search & retrieval engine
├── bm25_utils.py           # Shared tokenization for BM25
├── generation.py           # Stage 6: RAG answer generation with Groq API
├── evaluation.py           # Stage 7: Self-evaluation with 7 expert dimensions
│
├── data/
│   ├── raw/                # Source PDFs
│   │   ├── metadata.csv    # Document registry (filename, source, topic, hash)
│   │   └── *.pdf           # Original PDF files
│   │
│   ├── processed/          # Cleaned JSON (page-level text)
│   │   └── *.json          # One JSON per document
│   │
│   ├── chunks/             # Passage chunks
│   │   └── chunks.json     # All chunks with metadata
│   │
│   └── vectorstore/        # Search indices
│       ├── index.faiss     # FAISS dense vector index
│       ├── bm25_index.pkl  # BM25 inverted index
│       └── chunks_metadata.json  # Chunk metadata for result lookup
│
└── logs/
    └── preprocessing_log.csv  # Extraction status & stats per document
```

---

## Implementation Status

### ✅ Implemented (Phase 1-4)

| Component | Status | Description |
|-----------|--------|-------------|
| **Data Collection** | ✅ Complete | PDF registration, metadata logging, duplicate detection |
| **Preprocessing** | ✅ Complete | Text extraction, header/footer removal, cleaning |
| **Chunking** | ✅ Complete | Overlapping passage splitting (512 chars, 100 overlap) |
| **Dense Indexing** | ✅ Complete | FAISS IndexFlatIP with MiniLM-L6-v2 embeddings |
| **BM25 Indexing** | ✅ Complete | BM25Okapi keyword index |
| **Retrieval Engine** | ✅ Complete | Dense, BM25, and Hybrid (RRF) search modes |
| **CLI Interface** | ✅ Complete | Commands: collect, preprocess, chunk, index, search, ask |
| **Source Filtering** | ✅ Complete | Filter results by source (IPCC, FAO, etc.) |
| **LLM Answer Generation** | ✅ Complete | RAG pipeline with Groq API (Llama 3.3 70B) |
| **Citation Generation** | ✅ Complete | Inline citations linking to source documents |
| **Self-Evaluation** | ✅ Complete | 7-dimension expert evaluation (21 sub-criteria) |

### 🚧 Planned (Phase 5+)

| Component | Status | Description |
|-----------|--------|-------------|
| **Iterative Planning** | 📋 Planned | Agentic framework for multi-step reasoning |
| **Climate Data APIs** | 📋 Planned | Integration with My Climate View (89 endpoints) |
| **Location Disambiguation** | 📋 Planned | Convert location names to coordinates |
| **Multi-turn Conversations** | 📋 Planned | Dialogue-based interaction with context |
| **Web/App Frontend** | 📋 Planned | Interactive UI (Rust + WebAssembly per paper) |
| **User Feedback System** | 📋 Planned | Preference collection for model alignment |
| **OCR Support** | 📋 Planned | Handle scanned/image-based PDFs |

### 📊 Current Dataset

| Source | Documents | Status |
|--------|-----------|--------|
| IPCC AR6 Reports | 6 | ✅ Indexed |
| FAO Publications | 6 | ✅ Indexed |
| World Bank | 1 | ⚠️ Low text (needs OCR) |
| **Total Chunks** | ~5000+ | ✅ Searchable |

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- ~2GB disk space for embeddings and indices

### Installation

```bash
# Clone or navigate to project
cd MyClimateCopilot

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
```
pymupdf              # PDF text extraction
pandas               # Data handling
requests             # URL downloads
tqdm                 # Progress bars
sentence-transformers  # Embedding model
faiss-cpu            # Vector similarity search
rank_bm25            # Keyword search
groq                 # Groq API client for LLM inference
python-dotenv        # Environment variable management
```

---

## Usage Guide

### 1. Collect Documents

```bash
# Register local PDFs with source and topic metadata
python main.py collect --folder /path/to/pdfs --source FAO --topic "crop adaptation"

# Check collection status
python main.py summary
```

### 2. Preprocess Documents

```bash
# Extract and clean text from all registered PDFs
python main.py preprocess
```

### 3. Create Chunks

```bash
# Split documents into overlapping passages
python main.py chunk
```

### 4. Build Search Index

```bash
# Generate embeddings and build FAISS + BM25 indices
python main.py index
```

### 5. Search for Passages

```bash
# Dense (semantic) search
python main.py search -q "How will drought affect wheat yields?"

# BM25 (keyword) search
python main.py search -q "drought wheat yields" -m bm25

# Hybrid search (recommended)
python main.py search -q "climate change impact on agriculture" -m hybrid

# Filter by source
python main.py search -q "adaptation strategies" --source IPCC -m hybrid

# Adjust number of results
python main.py search -q "temperature projections" -k 10
```

### 6. Ask Questions (RAG Answer Generation)

```bash
# Basic question
python main.py ask -q "How will climate change affect wheat production?"

# With verbose output showing retrieval steps
python main.py ask -q "What are adaptation strategies for drought?" -v

# Show retrieved passages in output
python main.py ask -q "Impact of temperature on crop yields" --show-passages

# Filter by source and use different model
python main.py ask -q "IPCC findings on agriculture" --source IPCC --model llama3-8b-8192

# All options
python main.py ask -q "Your question" -k 10 --source FAO -m hybrid --model llama-3.3-70b-versatile -v --show-passages
```

### Example Output

**Search Command:**
```
==================================================
 [SEARCH] Query: 'How will climate change affect crop yields?' (mode: hybrid)
 Found 5 relevant passage(s)
==================================================

--- Result #1 [RRF Fused Score: 0.03226  [matched_by: dense, bm25]] ---
  Document: IPCC_AR6_WGII_SummaryForPolicymakers (IPCC_AR6_WGII_SummaryForPolicymakers.pdf)
  Source:   IPCC | Topic: climate impact assessment | Page: 12
  Passage:
  Climate change has already affected food security... agricultural productivity growth
  has slowed over the past 50 years globally...
```

**Ask Command (RAG):**
```
======================================================================
 MY CLIMATE COPILOT
======================================================================

📝 Question: How will climate change affect wheat production?

🤖 Model: llama-3.3-70b-versatile | Retrieval: hybrid
📊 Tokens: 1380 (prompt: 936, completion: 444)

----------------------------------------------------------------------

📖 ANSWER:

### Introduction to Climate Change Impact on Wheat Production
Climate change is expected to have significant impacts on agricultural production,
including wheat [1]. The effects of climate change on wheat production will vary
by region, with some areas potentially experiencing increased yields and others
facing declines [4].

### Regional Variations in Wheat Production
According to the IPCC, in many higher-latitude regions, yields of wheat have been
affected positively over recent decades due to climate change [4]...

----------------------------------------------------------------------

📚 SOURCES REFERENCED:
  [1] i3325e (FAO) - Page 208
  [2] i3325e (FAO) - Page 204
  [3] i3325e (FAO) - Page 208
  [4] SPM_Updated-Jan20 (IPCC) - Page 15
======================================================================
```

---

## Roadmap

### Phase 1-2: Retrieval Pipeline ✅
- [x] PDF collection & metadata management
- [x] Text extraction & preprocessing
- [x] Passage chunking with overlap
- [x] FAISS dense vector indexing
- [x] BM25 sparse indexing
- [x] Hybrid retrieval with RRF
- [x] CLI interface

### Phase 3: RAG Answer Generation ✅
- [x] LLM integration (Groq API with Llama 3.3 70B)
- [x] Prompt engineering for climate QA
- [x] Citation generation & linking
- [x] Response formatting with sources

### Phase 4: Evaluation & Feedback ✅
- [x] Self-evaluation with 7 expert dimensions (21 sub-criteria)
- [x] Dimension breakdown (Context, Structure, Language, Citations, Specificity, Comprehensiveness, Accuracy)
- [x] Visual score display with progress bar
- [ ] User feedback collection (positive/neutral/negative)
- [ ] Expert edit tracking for supervised tuning

### Phase 5: Advanced Features 📋
- [ ] Multi-turn conversation support
- [ ] Agentic iterative planning
- [ ] Climate data API integration (My Climate View)
- [ ] Location disambiguation
- [ ] Web/mobile frontend

---

## References

- **Paper**: *My Climate CoPilot: A Question Answering System for Climate Adaptation in Agriculture* (ACL 2025)
- **Authors**: Vincent Nguyen, Willow Hallgren, Ashley Harkin, Mahesh Prakash, Sarvnaz Karimi
- **Institutions**: CSIRO Data61, CSIRO Agriculture and Food, Bureau of Meteorology (Australia)

---

## License

This project is developed for research and educational purposes in climate science and NLP.
