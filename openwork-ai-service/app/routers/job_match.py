from __future__ import annotations

from fastapi import APIRouter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas import JobMatchRequest

router = APIRouter(tags=["job-match"])


_EXPERIENCE_SCORES = {
    "entry": 30.0,
    "junior": 35.0,
    "mid": 60.0,
    "intermediate": 60.0,
    "senior": 80.0,
    "expert": 95.0,
    "any": 50.0,
}


def _experience_score(level: str | None) -> float:
    return _EXPERIENCE_SCORES.get((level or "").lower().strip(), 50.0)


@router.post("/ai/job-match")
async def job_match(payload: JobMatchRequest):
    if not payload.jobs:
        return {"results": []}

    freelancer_text = " ".join(payload.freelancer.skills).strip() or "general"
    job_texts = [" ".join(j.skills).strip() or j.title or "general" for j in payload.jobs]

    # TfidfVectorizer raises if every document is empty; our fallbacks above prevent that.
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform([freelancer_text] + job_texts)
    except ValueError:
        # Vocabulary ended up empty (e.g. all stop words). Retry without stop-word filtering.
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform([freelancer_text] + job_texts)

    f_vec = matrix[0]
    f_exp = _experience_score(payload.freelancer.experience)

    results = []
    for i, job in enumerate(payload.jobs, start=1):
        j_vec = matrix[i]
        skill_score = float(cosine_similarity(f_vec, j_vec)[0][0]) * 100.0
        exp_score = 100.0 - abs(f_exp - _experience_score(job.experienceLevel))
        match = skill_score * 0.6 + exp_score * 0.4
        results.append(
            {
                "job": job.model_dump(),
                "matchScore": round(match, 2),
                "skillScore": round(skill_score, 2),
                "experienceScore": round(exp_score, 2),
            }
        )

    results.sort(key=lambda x: x["matchScore"], reverse=True)
    return {"results": results}
