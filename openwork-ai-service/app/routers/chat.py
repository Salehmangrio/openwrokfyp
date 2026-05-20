from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import ChatRequest
from app.services.openrouter import get_llm

router = APIRouter(tags=["chat"])


@router.post("/ai/chat")
async def chat(payload: ChatRequest):
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    system_msg = {
        "role": "system",
        "content": (
            "You are a career assistant for freelancers on OpenWork. "
            "Be concise, practical, and friendly. Do not include tables."
        ),
    }

    messages = [system_msg] + [m.model_dump() for m in payload.messages]

    answer = get_llm().chat(
        messages=messages,
        fallback="AI is temporarily unavailable. Please try again shortly.",
        temperature=0.7,
    )
    return {"message": answer}
