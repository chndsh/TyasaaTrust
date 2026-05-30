from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import APIRouter

try:
    from pydantic import BaseModel
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import BaseModel

from ..modules.psychometric import score_responses

router = APIRouter()

QUESTIONS: list[dict] = []


class QuizSubmission(BaseModel):
    merchant_id: str
    responses: list[dict] = []  # [{"question": str, "answer": str, "trait": str}]


@router.post("/submit")
async def submit_quiz(submission: QuizSubmission):
    responses = getattr(submission, "responses", []) or []
    result = score_responses(responses)
    return {
        "merchant_id": getattr(submission, "merchant_id", None),
        "psych_score": result.get("psych_score"),
        "traits": result.get("traits"),
        "summary": result.get("summary"),
    }


@router.get("/questions")
async def get_questions():
    return {"questions": QUESTIONS}
