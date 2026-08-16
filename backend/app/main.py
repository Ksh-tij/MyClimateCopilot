"""
FastAPI Application - My Climate CoPilot Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import ask, search, sources

# Create FastAPI app
app = FastAPI(
    title="My Climate CoPilot API",
    description="""
    A Question Answering System for Climate Adaptation in Agriculture.
    
    This API provides access to a RAG (Retrieval-Augmented Generation) system
    that answers questions about climate change impacts on agriculture using
    authoritative sources from IPCC, FAO, and other organizations.
    
    ## Features
    
    - **Ask**: Get AI-generated answers grounded in climate science literature
    - **Search**: Retrieve relevant passages from the knowledge base
    - **Evaluate**: Automatic quality assessment using expert criteria
    - **Sources**: View available documents in the knowledge base
    
    ## Retrieval Modes
    
    - `dense`: Semantic similarity search using sentence embeddings
    - `bm25`: Keyword-based search using BM25 algorithm
    - `hybrid`: Combines both using Reciprocal Rank Fusion (recommended)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ask.router, prefix="/api", tags=["Question Answering"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(sources.router, prefix="/api", tags=["System"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "My Climate CoPilot API",
        "version": "1.0.0",
        "description": "A Question Answering System for Climate Adaptation in Agriculture",
        "docs": "/docs",
        "health": "/api/health"
    }
