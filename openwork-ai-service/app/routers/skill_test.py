from __future__ import annotations

import logging
import random
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.data.fallback import quiz_data
from app.schemas import SkillEvaluateRequest, SkillTestGenerateRequest
from app.services.json_utils import safe_json_extract
from app.services.openrouter import get_llm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["skill-test"])


# ------------------------------------------------------------------ evaluate

def _evaluate_single(question: str, answer: str) -> Dict[str, Any]:
    raw = get_llm().chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict technical grader. Return ONLY a compact JSON "
                    'object with this shape: {"score": <integer 0-100>, "explanation": "<one short sentence>"}. '
                    "No prose, no markdown, no code fences."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\nCandidate answer: {answer}\nGrade the answer.",
            },
        ],
        fallback='{"score":50,"explanation":"Auto-scored fallback — AI grader unavailable."}',
        temperature=0.2,
        max_tokens=200,
        response_format={"type": "json_object"},
    )
    parsed = safe_json_extract(raw) or {}

    try:
        score = int(parsed.get("score", 50))
    except (TypeError, ValueError):
        score = 50
    score = max(0, min(100, score))

    explanation = str(parsed.get("explanation") or "No feedback provided.").strip()
    return {"score": score, "explanation": explanation}


@router.post("/ai/skill-test/evaluate")
async def evaluate(payload: SkillEvaluateRequest):
    if not payload.questions:
        raise HTTPException(status_code=400, detail="At least one question is required")
    if len(payload.answers) != len(payload.questions):
        raise HTTPException(status_code=400, detail="Mismatch in questions/answers length")

    results: List[Dict[str, Any]] = []
    total = 0
    for q, a in zip(payload.questions, payload.answers):
        graded = _evaluate_single(q, a)
        total += graded["score"]
        results.append(
            {
                "question": q,
                "answer": a,
                "score": graded["score"],
                "explanation": graded["explanation"],
            }
        )

    avg = round(total / len(payload.questions), 2)
    passed = avg >= 60
    return {
        "score": avg,
        "total": len(payload.questions),
        "percentage": avg,
        "passed": passed,
        "feedback": "Great job!" if passed else "Keep practicing and focus on clarity and correctness.",
        "aiScoreIncrease": 5 if passed else 0,
        "results": results,
    }


# ------------------------------------------------------------------ generate

def _normalize_question(raw: Any) -> Dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    question = str(raw.get("question", "")).strip()
    options = raw.get("options")
    answer = str(raw.get("answer") or raw.get("correct_answer") or "").strip()
    if not question or not isinstance(options, list) or len(options) != 4:
        return None
    options = [str(o).strip() for o in options if str(o).strip()]
    if len(options) != 4:
        return None
    if answer and answer not in options:
        # Try to fix capitalization/whitespace mismatch
        lowered = [o.lower() for o in options]
        if answer.lower() in lowered:
            answer = options[lowered.index(answer.lower())]
        else:
            answer = options[0]
    elif not answer:
        answer = options[0]
    return {"question": question, "options": options, "correct_answer": answer}


@router.post("/ai/skill-test/generate")
async def generate_skill_test(payload: SkillTestGenerateRequest) -> Dict[str, Any]:
    topic = (payload.topic or "").strip().lower()
    level = (payload.level or "easy").strip().lower()
    total = max(1, min(20, int(payload.total or 5)))

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    raw = get_llm().chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. Return ONLY a valid JSON object "
                    'with a single key "questions" whose value is an array. '
                    'Each array item must have keys "question" (string), '
                    '"options" (array of exactly 4 distinct strings), and '
                    '"answer" (string equal to one of the options). '
                    "No markdown, no prose, no code fences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate exactly {total} multiple-choice questions on the topic '{topic}' "
                    f"at '{level}' difficulty. Keep questions self-contained and unambiguous."
                ),
            },
        ],
        fallback='{"questions": []}',
        temperature=0.3,
        max_tokens=1600,
        response_format={"type": "json_object"},
    )
    logger.debug("skill-test raw: %s", raw)

    parsed = safe_json_extract(raw)
    candidate_items: List[Any] = []
    if isinstance(parsed, dict) and isinstance(parsed.get("questions"), list):
        candidate_items = parsed["questions"]
    elif isinstance(parsed, list):
        candidate_items = parsed

    questions: List[Dict[str, Any]] = []
    for item in candidate_items:
        norm = _normalize_question(item)
        if norm is not None:
            questions.append(norm)
        if len(questions) >= total:
            break

    # Fill gaps from the built-in fallback bank
    if len(questions) < total:
        filtered = [q for q in quiz_data if q.get("skill", "").lower() == topic]
        if level:
            leveled = [q for q in filtered if q.get("level", "").lower() == level]
            if leveled:
                filtered = leveled
        if not filtered:
            filtered = list(quiz_data)
        random.shuffle(filtered)
        for q in filtered:
            norm = _normalize_question(q)
            if norm is not None:
                questions.append(norm)
            if len(questions) >= total:
                break

    # Final hard fallback — never return empty.
    if not questions:
        questions = [
            {
                "question": f"Which best describes '{topic}'?",
                "options": [
                    "A programming concept",
                    "A tool or framework",
                    "A methodology",
                    "A database system",
                ],
                "correct_answer": "A programming concept",
            }
        ]

    return {
        "success": True,
        "topic": topic,
        "level": level,
        "total": len(questions[:total]),
        "questions": questions[:total],
    }
