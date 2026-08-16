"""
/api/sources and /api/health endpoints.
"""

from fastapi import APIRouter, HTTPException

from ..schemas.models import SourcesResponse, SourceInfo, HealthResponse
from ..services.rag_service import rag_service

router = APIRouter()

VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and index information.
    """
    index_loaded = rag_service.ensure_index_loaded()
    chunk_count = rag_service.get_chunk_count() if index_loaded else 0
    
    return HealthResponse(
        status="healthy" if index_loaded else "degraded",
        version=VERSION,
        index_loaded=index_loaded,
        chunk_count=chunk_count
    )


@router.get("/sources", response_model=SourcesResponse)
async def list_sources():
    """
    List available source documents.
    
    Returns information about all documents in the knowledge base.
    """
    try:
        sources = rag_service.get_sources()
        
        total_chunks = sum(s["chunk_count"] for s in sources)
        
        return SourcesResponse(
            total_documents=len(sources),
            total_chunks=total_chunks,
            documents=[
                SourceInfo(
                    filename=s["filename"],
                    title=s["title"],
                    source=s["source"],
                    topic=s["topic"],
                    chunk_count=s["chunk_count"]
                )
                for s in sources
            ]
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
