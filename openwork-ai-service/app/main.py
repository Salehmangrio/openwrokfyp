from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    chat,
    fraud,
    health,
    job_match,
    moderation,
    proposal,
    skill_suggestions,
    skill_test,
)

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="OpenWork AI Service",
    version="1.0.0",
    description="FastAPI micro-service that powers AI features for the OpenWork freelance marketplace using free OpenRouter models.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(proposal.router)
app.include_router(job_match.router)
app.include_router(skill_test.router)
app.include_router(fraud.router)
app.include_router(skill_suggestions.router)
app.include_router(moderation.router)


@app.get("/")
async def root():
    return {
        "service": "openwork-ai-service",
        "status": "ok" if settings.configured else "degraded",
        "docs": "/docs",
    }
