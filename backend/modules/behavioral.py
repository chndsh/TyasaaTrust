from typing import Any
import re

MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")


def _validate_merchant_id(merchant_id: str) -> None:
    if not MERCHANT_ID_PATTERN.match(merchant_id):
        raise ValueError("merchant_id must be a 10-digit numeric string.")


def get_behavioral_score(merchant_id: str) -> dict[str, Any]:
    _validate_merchant_id(merchant_id)

    from backend.data.mock_generator import generate_transactions
    txns = generate_transactions()

    events = [t for t in txns if t["initiating_merchant_id"] == merchant_id or t["receiving_merchant_id"] == merchant_id]
    footprint = summarize_digital_footprint(events)

    review_sentiment = 620 + (len(events) % 100)
    chargeback_rate = max(0, 40 - (len(events) // 10))

    return {
        "merchant_id": merchant_id,
        "behavioral_score": 600,
        "signals": {
            "review_sentiment": review_sentiment,
            "chargeback_rate": chargeback_rate,
        },
        "event_count": footprint["event_count"],
        "status": "scored",
    }


def summarize_digital_footprint(events: list[dict]) -> dict[str, Any]:
    event_count = min(len(events), 1000)
    return {
        "event_count": event_count,
        "summary": "stubbed digital footprint summary",
    }
