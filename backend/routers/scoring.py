from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.modules.behavioral import get_behavioral_score
from backend.modules.fusion import combine_scores
# Import the actual functions that exist in your psychometric module
from backend.modules.psychometric import score_session 
from backend.modules.social_graph import get_social_graph_score

router = APIRouter()

class ScoringPayload(BaseModel):
    session_id: str
    answers: dict[str, str]

@router.post("/score")
def score_merchant_session(payload: ScoringPayload):
    try:
        # 1. Score the active psychometric session from Redis
        psych_result = score_session(payload.session_id, payload.answers)
        merchant_id = psych_result["merchant_id"]
        
        # 2. Gather corresponding metrics from sister engines
        social_score = get_social_graph_score(merchant_id)
        behavioral_score = get_behavioral_score(merchant_id)
        
        # 3. Fuse the analytics vectors together
        return combine_scores(merchant_id, social_score, psych_result, behavioral_score)
        
    except KeyError as e:
        raise HTTPException(status_code=440, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))