from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---- Chat ----
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


# ---- Proposal ----
class GenerateProposalRequest(BaseModel):
    jobDescription: str
    freelancerProfile: Dict[str, Any] = Field(default_factory=dict)


# ---- Job match ----
class FreelancerProfile(BaseModel):
    skills: List[str] = Field(default_factory=list)
    aiScore: float = 0
    experience: str = "mid"
    location: str = ""
    completedJobs: int = 0
    rating: float = 0
    responseTimeHours: float = 24


class JobInput(BaseModel):
    id: Optional[str] = None
    title: str = ""
    skills: List[str] = Field(default_factory=list)
    experienceLevel: str = "mid"
    location: str = ""


class JobMatchRequest(BaseModel):
    freelancer: FreelancerProfile
    jobs: List[JobInput]


# ---- Skill test ----
class SkillEvaluateRequest(BaseModel):
    questions: List[str]
    answers: List[str]


class SkillTestGenerateRequest(BaseModel):
    topic: str
    level: str = "easy"
    total: int = 10


# ---- Fraud ----
class FraudDetectRequest(BaseModel):
    loginPatterns: List[float] = Field(default_factory=list)
    bidAmounts: List[float] = Field(default_factory=list)
    responseTimes: List[float] = Field(default_factory=list)


# ---- Skill suggestions ----
class SkillSuggestionsRequest(BaseModel):
    category: str
    query: str = ""


# ---- Moderation ----
class ModerationRequest(BaseModel):
    message: str


class ModerationResponse(BaseModel):
    verdict: Literal["SAFE", "UNSAFE"]
    reason: str = ""


# ---- Health ----
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model: str
