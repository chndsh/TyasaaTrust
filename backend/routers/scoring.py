try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import APIRouter

try:
    from pydantic import BaseModel, ConfigDict, Field
except Exception:  # pragma: no cover - optional dependency
    from .._stubs import BaseModel, Field, ConfigDict
from datetime import date
from typing import Any

from ..modules.behavioral import get_behavioral_score
from ..modules.fusion import combine_scores
from ..modules.psychometric import get_psychometric_score
from ..modules.social_graph import get_social_graph_score

router = APIRouter()

class ScoringPayload(BaseModel):
    session_id: str
    answers: dict[str, str]

class BehavioralScorePayload(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    account_id_hash: str
    as_of_date: date
    score: float
    model_version: str | None = None
    score_details: dict[str, Any] | None = None


class BehavioralScoreBatchPayload(BaseModel):
    scores: list[BehavioralScorePayload] = Field(default_factory=list)


class BehavioralScoreWriteResponse(BaseModel):
    status: str
    inserted: int


@router.get("/{merchant_id}")
def score_merchant(merchant_id: str):
    social = get_social_graph_score(merchant_id)
    psych = get_psychometric_score(merchant_id)
    behavioral = get_behavioral_score(merchant_id)
    return combine_scores(merchant_id, social, psych, behavioral)


@router.post("/behavioral", status_code=201, response_model=BehavioralScoreWriteResponse)
def write_behavioral_score_endpoint(payload: BehavioralScorePayload):
    # Lazy-import DB helpers to avoid import-time errors when SQLAlchemy/pandas
    # or other DB deps are not installed in the environment.
    try:
        from ..behavioral_proxies.utils.io import get_database_url
        from ..behavioral_proxies.utils.persistence import (
            build_database_engine,
            write_behavioral_score,
        )
    except Exception:
        return BehavioralScoreWriteResponse(status="error", inserted=0)

    try:
        engine = build_database_engine(get_database_url())
        inserted = write_behavioral_score(engine, payload.model_dump())
    except Exception:
        return BehavioralScoreWriteResponse(status="error", inserted=0)

    return BehavioralScoreWriteResponse(status="ok", inserted=inserted)


@router.post(
    "/behavioral/batch",
    status_code=201,
    response_model=BehavioralScoreWriteResponse,
)
def write_behavioral_scores_endpoint(payload: BehavioralScoreBatchPayload):
    try:
        from ..behavioral_proxies.utils.io import get_database_url
        from ..behavioral_proxies.utils.persistence import (
            build_database_engine,
            write_behavioral_scores,
        )
    except Exception:
        return BehavioralScoreWriteResponse(status="error", inserted=0)

    try:
        engine = build_database_engine(get_database_url())
        inserted = write_behavioral_scores(
            engine,
            [item.model_dump() for item in payload.scores],
        )
    except Exception:
        return BehavioralScoreWriteResponse(status="error", inserted=0)

    return BehavioralScoreWriteResponse(status="ok", inserted=inserted)
