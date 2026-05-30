from typing import Any


def combine_scores(
    merchant_id: str,
    social: dict[str, Any],
    psych: dict[str, Any],
    behavioral: dict[str, Any],
) -> dict[str, Any]:
    score_max = 1000

    def _score_value(payload: dict[str, Any], key: str) -> float:
        value = payload.get(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    scores = [
        _score_value(social, "social_score"),
        _score_value(psych, "psych_score"),
        _score_value(behavioral, "behavioral_score"),
    ]
    final_score = round(sum(scores) / max(len(scores), 1))
    final_score = max(0, min(score_max, final_score))

    return {
        "merchant_id": merchant_id,
        "final_score": final_score,
        "social_score": social.get("social_score"),
        "psych_score": psych.get("psych_score"),
        "behavioral_score": behavioral.get("behavioral_score"),
        "status": "stub",
    }
