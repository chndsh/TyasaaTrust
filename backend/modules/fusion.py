from typing import Any


def combine_scores(
    merchant_id: str,
    social: dict[str, Any],
    psych: dict[str, Any],
    behavioral: dict[str, Any],
) -> dict[str, Any]:
    scores = [
        social.get("social_score", 0.0),
        psych.get("psych_score", 0.0),
        behavioral.get("behavioral_score", 0.0),
    ]
    final_score = round(sum(scores) / max(len(scores), 1), 3)

    return {
        "merchant_id": merchant_id,
        "final_score": final_score,
        "social_score": social.get("social_score"),
        "psych_score": psych.get("psych_score"),
        "behavioral_score": behavioral.get("behavioral_score"),
        "status": "stub",
    }
