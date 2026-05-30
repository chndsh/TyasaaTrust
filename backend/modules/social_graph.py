from typing import Any
import re

MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")


def _validate_merchant_id(merchant_id: str) -> None:
    if not MERCHANT_ID_PATTERN.match(merchant_id):
        raise ValueError("merchant_id must be a 10-digit numeric string.")


def get_social_graph_score(merchant_id: str) -> dict[str, Any]:
    _validate_merchant_id(merchant_id)
    return {
        "merchant_id": merchant_id,
        "social_score": 620,
        "signals": {
            "connections": 18,
            "community_score": 700,
        },
        "status": "stub",
    }
