from typing import Any
import re

MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")


def _validate_merchant_id(merchant_id: str) -> None:
    if not MERCHANT_ID_PATTERN.match(merchant_id):
        raise ValueError("merchant_id must be a 10-digit numeric string.")


def get_behavioral_score(merchant_id: str) -> dict[str, Any]:
    _validate_merchant_id(merchant_id)
    return {
        "merchant_id": merchant_id,
        "behavioral_score": 600,
        "signals": {
            "review_sentiment": 630,
            "chargeback_rate": 40,
        },
        "status": "stub",
    }


def summarize_digital_footprint(events: list[dict]) -> dict[str, Any]:
    event_count = min(len(events), 1000)
    return {
        "event_count": event_count,
        "summary": "stubbed digital footprint summary",
    }
