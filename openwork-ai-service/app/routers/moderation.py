from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import ModerationRequest, ModerationResponse
from app.services.moderation import classify_message

router = APIRouter(tags=["moderation"])


@router.post("/ai/moderate", response_model=ModerationResponse)
async def moderate(payload: ModerationRequest) -> ModerationResponse:
    if payload.message is None:
        raise HTTPException(status_code=400, detail="message is required")
    verdict, reason = classify_message(payload.message)
    return ModerationResponse(verdict=verdict, reason=reason)
