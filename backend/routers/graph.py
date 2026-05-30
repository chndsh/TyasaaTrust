from typing import Annotated

from fastapi import APIRouter, Path

from backend.modules.social_graph import get_social_graph_score

router = APIRouter()


@router.get("/{merchant_id}")
def graph_score(
    merchant_id: Annotated[
        str,
        Path(
            pattern=r"^\d{10}$",
            description="10-digit merchant ID being assessed.",
            examples=["9800000000"],
        ),
    ],
):
    return get_social_graph_score(merchant_id)
