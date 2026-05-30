from fastapi import APIRouter

from modules.social_graph import get_social_graph_score

router = APIRouter()


@router.get("/{merchant_id}")
def graph_score(merchant_id: str):
    return get_social_graph_score(merchant_id)
