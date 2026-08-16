"""
/api/ask endpoint - Main Q&A endpoint.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

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


def _format_evaluation(eval_result: dict) -> Optional[EvaluationResponse]:
    """
    Convert raw evaluation to the response model.

    evaluate_response() keys its dimensions by display name ("Context") and uses
    the inner keys "subscores"/"max", while the API contract is keyed by criterion
    id ("1_context") with "subcriteria"/"max_score" and per-criterion descriptions.
    Rebuild from EVALUATION_CRITERIA so the canonical ids, order and descriptions
    are authoritative rather than inferred from the LLM response.
    """
    # evaluate_response() returns a flat {scores, feedback, error} dict when the
    # LLM output could not be parsed — there is nothing to score in that case.
    if eval_result.get("error") or "dimensions" not in eval_result:
        return None

    raw_dims = eval_result["dimensions"]
    dimensions = {}

    for dim_key, dim_meta in EVALUATION_CRITERIA.items():
        name = dim_meta["name"]
        raw = raw_dims.get(name) or raw_dims.get(dim_key) or {}
        # tolerate either key spelling so a later normalisation of evaluation.py
        # does not silently break this endpoint
        sub_raw = raw.get("subscores") or raw.get("subcriteria") or {}

        subcriteria = []
        for sub_code, description in dim_meta["subcriteria"].items():
            value = sub_raw.get(sub_code, 0)
            # values are plain 0/1 ints here, but accept the {score: n} shape too
            score = value.get("score", 0) if isinstance(value, dict) else value
            subcriteria.append(SubCriterionScore(
                code=sub_code,
                description=description,
                score=int(score)
            ))

        dimensions[dim_key] = DimensionScore(
            name=name,
            score=int(raw.get("score", sum(s.score for s in subcriteria))),
            max_score=int(raw.get("max_score") or raw.get("max") or 3),
            subcriteria=subcriteria
        )

    return EvaluationResponse(
        total_score=eval_result["total_score"],
        max_score=eval_result["max_score"],
        percentage=eval_result["percentage"],
        dimensions=dimensions,
        feedback=eval_result.get("feedback", "")
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
                passages=result["passages"],
                # honour an explicitly requested model for evaluation too,
                # otherwise a per-request override would silently apply to
                # generation only and still hit the original model's quota
                model=request.model
            )
            response.evaluation = _format_evaluation(eval_result)
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
