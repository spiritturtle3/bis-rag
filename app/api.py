from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field
from tempfile import NamedTemporaryFile
from pathlib import Path

from app.rag.recommendation import recommend_standards
from app.rag.tender_recommendation import recommend_from_tender
from app.rag.llm_generator import generate_answer
from app.rag.frontend_formatter import format_frontend_response


router = APIRouter()


class RecommendationRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language procurement requirement",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class RecommendationResponse(BaseModel):
    query: str
    recommendations: list[dict]


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
)
def recommend(request: RecommendationRequest):
    recommendations = recommend_standards(
        request.query,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "recommendations": recommendations,
    }


@router.post("/recommend/llm")
def recommend_with_llm(
    query: str = Form(...),
    limit: int = Form(5),
):
    result = recommend_from_tender(
        query=query,
        limit=limit,
    )

    answer = generate_answer(
        query=result["query"],
        recommendations=result["recommendations"],
        evidence=result["evidence"],
    )

    return format_frontend_response(
        query=result["query"],
        recommendations=result["recommendations"],
        answer=answer,
    )


@router.post("/recommend/llm/tender")
async def recommend_tender_with_llm(
    file: UploadFile = File(...),
    query: str = Form(""),
    limit: int = Form(5),
):
    suffix = Path(file.filename or "").suffix or ".pdf"

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        result = recommend_from_tender(
            query=query or None,
            pdf_path=temp_path,
            limit=limit,
        )

        answer = generate_answer(
            query=result["query"],
            recommendations=result["recommendations"],
            evidence=result["evidence"],
        )

        response = format_frontend_response(
            query=result["query"],
            recommendations=result["recommendations"],
            answer=answer,
        )

        tender_requirements = dict(
            result.get("tenderRequirements") or {}
        )

        tender_requirements.pop("rawText", None)

        response["tenderRequirements"] = tender_requirements

        return response

    finally:
        Path(temp_path).unlink(missing_ok=True)