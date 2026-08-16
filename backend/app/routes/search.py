"""
/api/search endpoint - Retrieve passages without generation.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.models import SearchRequest, SearchResponse, PassageResponse
from ..services.rag_service import rag_service

router = APIRouter()


def _format_passages(passages: List[dict]) -> List[PassageResponse]:
    """Convert raw passages to response model."""
    return [
        PassageResponse(
            chunk_id=p["chunk_id"],
            title=p["title"],
            source=p["source"],
            topic=p["topic"],
            page_number=p["page_number"],
            text=p["text"],
            score=p["score"],
            doc_filename=p["doc_filename"],
            mode=p["mode"],
            matched_by=p.get("matched_by")
        )
        for p in passages
    ]


@router.post("/search", response_model=SearchResponse)
async def search_passages(request: SearchRequest):
    """
    Search for relevant passages in the knowledge base.
    
    Returns retrieved passages without generating an answer.
    """
    try:
        passages = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            mode=request.mode,
            source_filter=request.source_filter
        )
        
        return SearchResponse(
            query=request.query,
            mode=request.mode,
            count=len(passages),
            passages=_format_passages(passages)
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
