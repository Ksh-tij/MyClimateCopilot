"""
Pydantic models for API request/response validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ Request Models ============

class AskRequest(BaseModel):
    """Request body for /api/ask endpoint."""
    query: str = Field(..., min_length=1, description="User's question about climate adaptation")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of passages to retrieve")
    mode: str = Field(default="hybrid", description="Retrieval mode: dense, bm25, or hybrid")
    source_filter: Optional[str] = Field(default=None, description="Filter by source (e.g., IPCC, FAO)")
    include_sources: bool = Field(default=True, description="Include retrieved passages in response")
    include_evaluation: bool = Field(default=False, description="Include self-evaluation scores")
    model: str = Field(default="llama-3.3-70b-versatile", description="Groq model to use")


class SearchRequest(BaseModel):
    """Request body for /api/search endpoint."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of passages to retrieve")
    mode: str = Field(default="hybrid", description="Retrieval mode: dense, bm25, or hybrid")
    source_filter: Optional[str] = Field(default=None, description="Filter by source")


# ============ Response Models ============

class PassageResponse(BaseModel):
    """A single retrieved passage."""
    chunk_id: str
    title: str
    source: str
    topic: str
    page_number: int
    text: str
    score: float
    doc_filename: str
    mode: str
    matched_by: Optional[List[str]] = None


class SubCriterionScore(BaseModel):
    """Score for a single sub-criterion."""
    code: str
    description: str
    score: int  # 0 or 1


class DimensionScore(BaseModel):
    """Score for an evaluation dimension."""
    name: str
    score: int
    max_score: int = 3
    subcriteria: List[SubCriterionScore]


class EvaluationResponse(BaseModel):
    """Evaluation results."""
    total_score: int
    max_score: int = 21
    percentage: float
    dimensions: Dict[str, DimensionScore]
    feedback: str


class UsageStats(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AskResponse(BaseModel):
    """Response from /api/ask endpoint."""
    question: str
    answer: str
    model: str
    retrieval_mode: str
    usage: UsageStats
    sources: Optional[List[PassageResponse]] = None
    evaluation: Optional[EvaluationResponse] = None


class SearchResponse(BaseModel):
    """Response from /api/search endpoint."""
    query: str
    mode: str
    count: int
    passages: List[PassageResponse]


class SourceInfo(BaseModel):
    """Information about a source document."""
    filename: str
    title: str
    source: str
    topic: str
    chunk_count: int


class SourcesResponse(BaseModel):
    """Response from /api/sources endpoint."""
    total_documents: int
    total_chunks: int
    documents: List[SourceInfo]


class HealthResponse(BaseModel):
    """Response from /api/health endpoint."""
    status: str
    version: str
    index_loaded: bool
    chunk_count: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
