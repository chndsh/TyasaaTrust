from typing import Any


def get_social_graph_score(merchant_id: str) -> dict[str, Any]:
    return {
        "merchant_id": merchant_id,
        "social_score": 0.62,
        "signals": {
            "connections": 18,
            "community_score": 0.7,
        },
        "status": "stub",
    }
