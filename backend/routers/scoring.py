from fastapi import APIRouter

from backend.modules.behavioral import get_behavioral_score
from backend.modules.fusion import combine_scores
from backend.modules.psychometric import get_psychometric_score
from backend.modules.social_graph import get_social_graph_score

router = APIRouter()


@router.get("/{merchant_id}")
def score_merchant(merchant_id: str):
    social = get_social_graph_score(merchant_id)
    psych = get_psychometric_score(merchant_id)
    behavioral = get_behavioral_score(merchant_id)
    return combine_scores(merchant_id, social, psych, behavioral)
