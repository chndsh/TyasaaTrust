try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import APIRouter
from typing import Annotated
try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import BaseModel, Field

from ..modules.behavioral import summarize_digital_footprint

router = APIRouter()
MERCHANT_ID_PATTERN = r"^\d{10}$"
MerchantId = Annotated[
    str,
    Field(
        ...,
        pattern=MERCHANT_ID_PATTERN,
        description="10-digit numeric merchant identifier.",
        examples=["9800000000"],
    ),
]


class DigitalFootprintPayload(BaseModel):
    merchant_id: MerchantId
    events: list[dict] = Field(default_factory=list)


@router.post("/digital-footprint")
def ingest_digital_footprint(payload: DigitalFootprintPayload):
    events = getattr(payload, "events", []) or []
    summary = summarize_digital_footprint(events)
    return {
        "merchant_id": getattr(payload, "merchant_id", None),
        "summary": summary,
        "status": "stub",
    }
