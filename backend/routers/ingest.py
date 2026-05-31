from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.modules.behavioral import summarize_digital_footprint

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
    summary = summarize_digital_footprint(payload.events)
    return {
        "merchant_id": payload.merchant_id,
        "summary": summary,
        "status": "stub",
    }
