from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from app.schemas import SkillSuggestionsRequest
from app.services.json_utils import safe_json_extract
from app.services.openrouter import get_llm

router = APIRouter(tags=["skill-suggestions"])


_STATIC_SUGGESTIONS: Dict[str, List[Dict[str, object]]] = {
    "backend": [
        {"skill": "Python", "demand": 95},
        {"skill": "FastAPI", "demand": 88},
        {"skill": "PostgreSQL", "demand": 85},
        {"skill": "Docker", "demand": 82},
        {"skill": "Node.js", "demand": 80},
    ],
    "frontend": [
        {"skill": "React", "demand": 94},
        {"skill": "TypeScript", "demand": 90},
        {"skill": "Next.js", "demand": 86},
        {"skill": "Tailwind CSS", "demand": 80},
        {"skill": "Vite", "demand": 72},
    ],
    "mobile": [
        {"skill": "React Native", "demand": 88},
        {"skill": "Swift", "demand": 82},
        {"skill": "Kotlin", "demand": 80},
        {"skill": "Flutter", "demand": 78},
    ],
    "data": [
        {"skill": "SQL", "demand": 93},
        {"skill": "Python", "demand": 90},
        {"skill": "Pandas", "demand": 85},
        {"skill": "dbt", "demand": 70},
        {"skill": "Airflow", "demand": 68},
    ],
    "ai": [
        {"skill": "Python", "demand": 96},
        {"skill": "PyTorch", "demand": 88},
        {"skill": "LangChain", "demand": 80},
        {"skill": "Vector Databases", "demand": 78},
        {"skill": "Prompt Engineering", "demand": 75},
    ],
}


def _static_for(category: str) -> List[Dict[str, object]]:
    return _STATIC_SUGGESTIONS.get(category.lower(), _STATIC_SUGGESTIONS["backend"])


@router.post("/ai/skill-suggestions")
async def skills(payload: SkillSuggestionsRequest):
    category = (payload.category or "").strip().lower() or "backend"
    query = (payload.query or "").strip()

    fallback = _static_for(category)

    raw = get_llm().chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You recommend in-demand freelance skills. Return ONLY a JSON object with key "
                    '"suggestions" whose value is an array of 5 items shaped '
                    '{"skill": "<string>", "demand": <integer 0-100>}. '
                    "No prose, no markdown."
                ),
            },
            {
                "role": "user",
                "content": f"Category: {category}. Freelancer interest: {query or 'general'}.",
            },
        ],
        fallback='{"suggestions": []}',
        temperature=0.4,
        max_tokens=400,
        response_format={"type": "json_object"},
    )

    parsed = safe_json_extract(raw) or {}
    suggestions = parsed.get("suggestions") if isinstance(parsed, dict) else None

    cleaned: List[Dict[str, object]] = []
    if isinstance(suggestions, list):
        for item in suggestions:
            if not isinstance(item, dict):
                continue
            skill = str(item.get("skill", "")).strip()
            demand_raw = item.get("demand", 0)
            try:
                demand = int(demand_raw)
            except (TypeError, ValueError):
                demand = 0
            demand = max(0, min(100, demand))
            if skill:
                cleaned.append({"skill": skill, "demand": demand})
            if len(cleaned) >= 5:
                break

    if not cleaned:
        cleaned = fallback

    return {"suggestions": cleaned[:5]}
