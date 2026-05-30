from typing import Any


def score_responses(responses: list[dict]) -> dict[str, Any]:
    if not responses:
        return {
            "psych_score": 0.55,
            "traits": {"openness": 0.5, "conscientiousness": 0.6},
            "summary": "stubbed (no responses provided)",
        }

    score = min(0.4 + (len(responses) * 0.05), 0.95)
    return {
        "psych_score": round(score, 2),
        "traits": {"openness": 0.58, "conscientiousness": 0.62},
        "summary": "stubbed from response count",
    }


def get_psychometric_score(merchant_id: str) -> dict[str, Any]:
    return {
        "merchant_id": merchant_id,
        "psych_score": 0.57,
        "traits": {"openness": 0.6, "conscientiousness": 0.55},
        "status": "stub",
    }
