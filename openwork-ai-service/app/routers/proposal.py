from __future__ import annotations

import json

from fastapi import APIRouter

from app.schemas import GenerateProposalRequest
from app.services.openrouter import get_llm

router = APIRouter(tags=["proposal"])


_FALLBACK = (
    "I'm confident I can deliver this project with high quality, clear "
    "communication, and on-time delivery. Looking forward to discussing the "
    "specifics with you."
)


@router.post("/ai/generate-proposal")
async def generate_proposal(payload: GenerateProposalRequest):
    profile_json = json.dumps(payload.freelancerProfile, default=str, ensure_ascii=False)

    proposal = get_llm().chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Write a concise, persuasive freelance proposal under 180 words. "
                    "Use first-person voice. No greetings like 'Dear client'. "
                    "Reference the job requirements and how the profile fits. "
                    "Do not invent credentials the profile does not mention."
                ),
            },
            {
                "role": "user",
                "content": f"Job description:\n{payload.jobDescription}\n\nFreelancer profile JSON:\n{profile_json}",
            },
        ],
        fallback=_FALLBACK,
        temperature=0.6,
        max_tokens=400,
    )
    # Normalize whitespace and cap length to avoid runaway model output.
    cleaned = " ".join(proposal.split())[:1200]
    return {"proposal": cleaned}
