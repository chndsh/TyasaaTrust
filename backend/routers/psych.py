from fastapi import APIRouter
from pydantic import BaseModel

from ..modules.psychometric import score_responses

router = APIRouter()

QUESTIONS: list[dict] = []

class QuizSubmission(BaseModel):
    merchant_id: str
    responses: list[dict]   # [{"question": str, "answer": str, "trait": str}]

@router.post("/submit")
async def submit_quiz(submission: QuizSubmission):
    result = score_responses(submission.responses)
    return {
        "merchant_id": submission.merchant_id,
        "psych_score": result["psych_score"],
        "traits": result["traits"],
        "summary": result["summary"]
    }

@router.get("/questions")
async def get_questions():
    return {"questions": QUESTIONS}