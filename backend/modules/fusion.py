from typing import Any


def combine_scores(
    merchant_id: str,
    social: dict[str, Any],
    psych: dict[str, Any],
    behavioral: dict[str, Any],
) -> dict[str, Any]:
    scores = [
        float(social.get("social_score", 0.0)),
        float(psych.get("psych_score", 0.0)),
        float(behavioral.get("behavioral_score", 0.0)),
    ]
    average_score = sum(scores) / max(len(scores), 1)
    final_score = max(0, min(1000, round(average_score)))

    return {
        "merchant_id": merchant_id,
        "final_score": final_score,
        "social_score": social.get("social_score"),
        "psych_score": psych.get("psych_score"),
        "behavioral_score": behavioral.get("behavioral_score"),
        "status": "stub",
    }
