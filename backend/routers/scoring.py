from fastapi import APIRouter

from modules.behavioral import get_behavioral_score
from modules.fusion import combine_scores
from modules.psychometric import get_psychometric_score
from modules.social_graph import get_social_graph_score

router = APIRouter()


@router.get("/{merchant_id}")
async def score_merchant(merchant_id: str):
    social = get_social_graph_score(merchant_id)
    psych = get_psychometric_score(merchant_id)
    behavioral = get_behavioral_score(merchant_id)
    return combine_scores(merchant_id, social, psych, behavioral)
