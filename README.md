# 🌿 My Climate CoPilot

A **Retrieval-Augmented Generation (RAG)** Question Answering system for climate adaptation in agriculture. Built based on the ACL 2025 paper: *"My Climate CoPilot: A Question Answering System for Climate Adaptation in Agriculture"*.

## ✨ Features

- **Hybrid Search**: Combines semantic (FAISS) and keyword (BM25) retrieval with Reciprocal Rank Fusion
- **Grounded Answers**: LLM responses cite specific passages from authoritative climate documents
- **Self-Evaluation**: 7-dimension quality assessment with 21 expert-defined criteria
- **Full-Stack Web UI**: React frontend with FastAPI backend
- **CLI Interface**: Command-line tools for all operations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MY CLIMATE COPILOT                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   Frontend   │────▶️│   Backend    │────▶️│ RAG Pipeline │            │
│  │   (React)    │◀️────│  (FastAPI)   │◀️────│              │            │
│  │  Port 3000   │     │  Port 8000   │     │              │            │
│  └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                    │
│         ┌──────────────────────────────────────────┼───────────┐       │
│         │                                          │           │       │
│         ▼                                          ▼           ▼       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ ┌───────────┐  │
│  │   FAISS     │    │    BM25     │    │    Groq     │ │ Evaluator │  │
│  │  (Dense)    │    │ (Keyword)   │    │    LLM      │ │ (7-dim)   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘ └───────────┘  │
│         │                  │                                           │
│         └────────┬─────────┘                                           │
│                  ▼                                                     │
│         ┌─────────────────┐                                            │
│         │ Reciprocal Rank │                                            │
│         │     Fusion      │                                            │
│         └─────────────────┘                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
PDFs (IPCC, FAO, etc.)
        │
        ▼
┌───────────────────┐
│  1. Collection    │  Register PDFs, extract metadata
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  2. Preprocessing │  PyMuPDF extraction, clean text
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  3. Chunking      │  Split into ~500 token passages
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  4. Indexing      │  FAISS vectors + BM25 index
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  5. Retrieval     │  Hybrid search with RRF
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  6. Generation    │  Groq LLM with citations
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  7. Evaluation    │  7-dimension quality scoring
└───────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Groq API key ([get one free](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/anusanth26/MyClimateCopilot.git
cd MyClimateCopilot

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### Run the Web UI

```bash
# Terminal 1: Start backend (port 8000)
cd backend && python run.py

# Terminal 2: Start frontend (port 3000)
cd frontend && npm run dev
```

Open **http://localhost:3000** in your browser.

### Run via CLI

```bash
# Ask a question
python main.py ask -q "How will climate change affect wheat production?"

# With evaluation
python main.py ask -q "What are adaptation strategies for rice?" --eval

# Search passages only
python main.py search -q "drought resistant crops" -k 10
```

## 📁 Project Structure

```
MyClimateCopilot/
├── main.py                 # CLI entry point
├── config.py               # Paths and settings
├── data_collection.py      # PDF registration
├── preprocessing.py        # Text extraction and cleaning
├── chunking.py             # Passage splitting
├── indexing.py             # FAISS + BM25 index building
├── retrieval.py            # Hybrid search engine
├── generation.py           # RAG answer generation
├── evaluation.py           # 7-dimension self-evaluation
├── bm25_utils.py           # BM25 tokenization utilities
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in git)
│
├── backend/                # FastAPI REST API
│   ├── app/
│   │   ├── main.py         # FastAPI app with CORS
│   │   ├── routes/
│   │   │   ├── ask.py      # POST /api/ask
│   │   │   ├── search.py   # POST /api/search
│   │   │   └── sources.py  # GET /api/health, /api/sources
│   │   ├── schemas/
│   │   │   └── models.py   # Pydantic models
│   │   └── services/
│   │       └── rag_service.py
│   └── run.py              # Server entry point
│
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # HomePage, AboutPage
│   │   ├── services/       # API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── raw/                # Source PDFs + metadata.csv
│   ├── processed/          # Cleaned JSON per document
│   ├── chunks/             # Chunked passages
│   └── vectorstore/        # FAISS index + BM25 index
│
└── logs/                   # Processing logs
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ask` | POST | Ask a question, get AI answer with citations |
| `/api/search` | POST | Retrieve relevant passages |
| `/api/sources` | GET | List available documents |
| `/api/health` | GET | System health check |

**Interactive docs:** http://localhost:8000/docs

### Example Request

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does climate change affect crop yields?",
    "top_k": 5,
    "mode": "hybrid",
    "include_evaluation": true
  }'
```

## 📚 CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py collect --folder <path> --source <name>` | Register PDFs |
| `python main.py preprocess` | Extract and clean text |
| `python main.py summary` | Show document statistics |
| `python main.py chunk` | Split into passages |
| `python main.py index` | Build FAISS + BM25 indexes |
| `python main.py search -q <query>` | Search passages |
| `python main.py ask -q <query>` | Get AI answer |
| `python main.py ask -q <query> --eval` | With evaluation |

## 📏 Evaluation Framework

Responses are scored across **7 dimensions** with **21 sub-criteria**:

| Dimension | Description |
|-----------|-------------|
| **Context** | Provides background, intro, and summary |
| **Structure** | Well-organized with headings and bullets |
| **Language** | Clear, grammatically correct, domain-appropriate |
| **Citations** | Properly referenced sources |
| **Specificity** | Location and commodity-specific details |
| **Comprehensiveness** | Complete, in-depth coverage |
| **Scientific Accuracy** | Factually correct, evidence-based |

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Vector Search** | FAISS (IndexFlatIP) |
| **Keyword Search** | BM25Okapi |
| **Fusion** | Reciprocal Rank Fusion (RRF) |
| **LLM** | Groq API (llama-3.3-70b-versatile) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | React 18 + Vite |
| **PDF Extraction** | PyMuPDF |

## 📖 Knowledge Base

Current sources include:
- IPCC AR5 & AR6 Reports
- FAO Climate Change Guidelines
- WMO Climate Science Reports
- Regional Adaptation Studies

## 🔄 Adding New Documents

```bash
# 1. Place PDF in data/raw/
# 2. Register and process
python main.py collect --folder data/raw --source "IPCC" --topic "adaptation"
python main.py preprocess
python main.py chunk
python main.py index

# 3. Restart backend to load new index
```

## ✅ Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Done | Data collection & PDF registration |
| Phase 2 | ✅ Done | Preprocessing, chunking, indexing |
| Phase 3 | ✅ Done | RAG answer generation with Groq |
| Phase 4 | ✅ Done | Self-evaluation (7 dimensions) |
| Phase 5 | ✅ Done | Full-stack Web UI |

## 📄 License

MIT License

## 🙏 Acknowledgments

Based on the ACL 2025 paper: *"My Climate CoPilot: A Question Answering System for Climate Adaptation in Agriculture"*
