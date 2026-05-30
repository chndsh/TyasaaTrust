from fastapi import APIRouter
from pydantic import BaseModel
from modules.psychometric import score_responses

router = APIRouter()

class QuizSubmission(BaseModel):
    merchant_id: str
    responses: list[dict]   # [{"question": str, "answer": str, "trait": str}]

@router.post("/submit")
def submit_quiz(submission: QuizSubmission):
    result = score_responses(submission.responses)
    return {
        "merchant_id": submission.merchant_id,
        "psych_score": result["psych_score"],
        "traits": result["traits"],
        "summary": result["summary"]
    }

@router.get("/questions")
def get_questions():
    from data.questions import QUESTIONS
    return {"questions": QUESTIONS}