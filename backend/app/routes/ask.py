"""
/api/ask endpoint - Main Q&A endpoint.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas.models import (
    AskRequest, AskResponse, PassageResponse, 
    EvaluationResponse, DimensionScore, SubCriterionScore, UsageStats
)
from ..services.rag_service import rag_service
from evaluation import EVALUATION_CRITERIA

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
            similarity=p.get("similarity"),
            doc_filename=p["doc_filename"],
            mode=p["mode"],
            matched_by=p.get("matched_by")
        )
        for p in passages
    ]


def _format_evaluation(eval_result: dict) -> EvaluationResponse:
    """Convert raw evaluation to response model."""
    dimensions = {}
    
    for dim_key, dim_data in eval_result["dimensions"].items():
        subcriteria = []
        for sub_code, sub_info in dim_data["subcriteria"].items():
            subcriteria.append(SubCriterionScore(
                code=sub_code,
                description=sub_info["description"],
                score=sub_info["score"]
            ))
        
        dimensions[dim_key] = DimensionScore(
            name=dim_data["name"],
            score=dim_data["score"],
            max_score=dim_data["max_score"],
            subcriteria=subcriteria
        )
    
    return EvaluationResponse(
        total_score=eval_result["total_score"],
        max_score=eval_result["max_score"],
        percentage=eval_result["percentage"],
        dimensions=dimensions,
        feedback=eval_result["feedback"]
    )


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about climate adaptation in agriculture.
    
    Returns a generated answer with optional sources and evaluation.
    """
    try:
        # Generate answer
        result = rag_service.generate_answer(
            question=request.query,
            top_k=request.top_k,
            mode=request.mode,
            source_filter=request.source_filter,
            model=request.model
        )
        
        # Build response
        response = AskResponse(
            question=result["question"],
            answer=result["answer"],
            model=result["model"],
            retrieval_mode=result["retrieval_mode"],
            usage=UsageStats(**result["usage"]),
            sources=_format_passages(result["passages"]) if request.include_sources else None,
            evaluation=None
        )
        
        # Optional: Run evaluation
        if request.include_evaluation:
            eval_result = rag_service.evaluate_answer(
                question=result["question"],
                answer=result["answer"],
                passages=result["passages"]
            )
            response.evaluation = _format_evaluation(eval_result)
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
