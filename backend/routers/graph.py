try:
    from fastapi import APIRouter, Path
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import APIRouter

from ..modules.social_graph import get_social_graph_score

router = APIRouter()
MERCHANT_ID_PATTERN = r"^\d{10}$"


@router.get("/{merchant_id}")
def graph_score(
    merchant_id: str = Path(
        ...,
        pattern=MERCHANT_ID_PATTERN,
        description="10-digit numeric merchant identifier.",
        examples=["9800000000"],
    )
):
    return get_social_graph_score(merchant_id)
