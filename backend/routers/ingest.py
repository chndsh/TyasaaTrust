from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.modules.behavioral import summarize_digital_footprint

router = APIRouter()


class DigitalFootprintPayload(BaseModel):
    merchant_id: str
    events: list[dict] = Field(default_factory=list)


@router.post("/digital-footprint")
def ingest_digital_footprint(payload: DigitalFootprintPayload):
    summary = summarize_digital_footprint(payload.events)
    return {
        "merchant_id": payload.merchant_id,
        "summary": summary,
        "status": "stub",
    }
