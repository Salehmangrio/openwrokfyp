from __future__ import annotations

from fastapi import APIRouter

from app.schemas import HealthResponse
from app.services.openrouter import get_llm

router = APIRouter(tags=["health"])


@router.get("/ai/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    llm = get_llm()
    return HealthResponse(
        status="ok" if llm.configured else "degraded",
        service="python-ai",
        version="1.0.0",
        model=llm.primary_model,
    )
