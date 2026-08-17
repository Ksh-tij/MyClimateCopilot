# MyClimateCopilot — End-to-End Setup & Execution Guide

Complete guide for setup, pipeline execution, backend server, and frontend web application — designed so anyone can set up and run the project from scratch.

---

## 📋 Prerequisites
- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js**: 18+ and `npm`

---

## 🚀 1. First-Time Environment Setup

### Step A: Clone / Open Repository
Open your terminal in the project directory:

```bash
cd MyClimateCopilot
```

### Step B: Set Up Python Virtual Environment
Create and activate a Python virtual environment:

#### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step C: Install Python Dependencies
Install all backend and NLP pipeline packages:

```bash
pip install -r requirements.txt
```

### Step D: Configure Environment Variables
Copy `.env.example` to `.env` (or create a `.env` file in the root directory):

```bash
cp .env.example .env
```

Ensure your `.env` file has your Groq API Key if using generation features:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### Step E: Install Frontend Dependencies
Navigate to the `frontend` directory and install npm packages:

```bash
cd frontend
npm install
cd ..
```

---

## ⚙️ 2. Build NLP Pipeline Data (Run Once)

Before starting the web app, build the preprocessed documents, passage chunks, and vector index. Run these from the project root (`MyClimateCopilot`):

```bash
# 1. Preprocess raw PDFs -> clean page JSONs
python main.py preprocess

# 2. Split preprocessed JSONs -> passage chunks
python main.py chunk

# 3. Generate embeddings & build FAISS + BM25 indices
python main.py index
```

---

## 🌐 3. Starting the Application

### Terminal 1: Backend Server (FastAPI)
From the project root directory (`MyClimateCopilot`), make sure your virtual environment is active and run:

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`

---

### Terminal 2: Frontend Web UI (React + Vite)
Open a **new terminal window**, navigate to `frontend/`, and start the development server:

```bash
cd frontend
npm run dev
```
- **Frontend Web App**: `http://localhost:5173`

---

## 🧪 4. Testing Search via CLI (Optional)

You can also test semantic search directly from the command line:

```bash
# General search
python main.py search --query "What are crop adaptation strategies for drought?" --top_k 5

# Source-filtered search (e.g. IPCC or FAO)
python main.py search --query "greenhouse gas emissions" --top_k 3 --source IPCC
```

---

## 📂 Troubleshooting & Common Fixes

| Issue | Solution |
|:---|:---|
| `ModuleNotFoundError: No module named 'app'` | Run uvicorn using `backend.app.main:app` (with `backend.` prefix) when in root directory. |
| `No module named 'pymupdf'` | Activate virtual environment (`.\.venv\Scripts\Activate`) and run `pip install -r requirements.txt`. |
| `vite: command not found` | Navigate to `frontend` folder (`cd frontend`) and run `npm install`. |
