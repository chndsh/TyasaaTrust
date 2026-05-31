from typing import Any

SCORE_SCALE = 1000
SOCIAL_WEIGHT = 0.5
BEHAVIORAL_WEIGHT = 0.3
PSYCH_WEIGHT = 0.2


def combine_scores(
    merchant_id: str,
    social: dict[str, Any],
    psych: dict[str, Any],
    behavioral: dict[str, Any],
) -> dict[str, Any]:
    social_score = int(social.get("social_score", 0))
    psych_score = int(psych.get("psych_score", 0))
    behavioral_score = int(behavioral.get("behavioral_score", 0))
    final_score = int(round(
        (social_score * SOCIAL_WEIGHT)
        + (behavioral_score * BEHAVIORAL_WEIGHT)
        + (psych_score * PSYCH_WEIGHT)
    ))
    final_score = max(0, min(final_score, SCORE_SCALE))

    return {
        "merchant_id": merchant_id,
        "final_score": final_score,
        "social_score": social_score,
        "psych_score": psych_score,
        "behavioral_score": behavioral_score,
        "status": "stub",
    }
