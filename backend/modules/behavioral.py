from typing import Any


def get_behavioral_score(merchant_id: str) -> dict[str, Any]:
    return {
        "merchant_id": merchant_id,
        "behavioral_score": 600,
        "signals": {
            "review_sentiment": 0.63,
            "chargeback_rate": 0.04,
        },
        "status": "stub",
    }


def summarize_digital_footprint(events: list[dict]) -> dict[str, Any]:
    return {
        "event_count": len(events),
        "summary": "stubbed digital footprint summary",
    }
