from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Column, Date, DateTime, Integer, MetaData, Numeric, Table, Text, create_engine, func, insert

from .io import get_database_url

metadata = MetaData()

behavioral_scores_table = Table(
    "behavioral_scores",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("account_id_hash", Text, nullable=False),
    Column("as_of_date", Date, nullable=False),
    Column("score", Numeric(6, 4), nullable=False),
    Column("model_version", Text, nullable=True),
    Column("score_details", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


def build_database_engine(database_url: str | None = None):
    return create_engine(database_url or get_database_url())


def _normalize_score_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)

    as_of_date = normalized.get("as_of_date")
    if isinstance(as_of_date, str):
        normalized["as_of_date"] = date.fromisoformat(as_of_date)
    elif isinstance(as_of_date, datetime):
        normalized["as_of_date"] = as_of_date.date()

    score_details = normalized.get("score_details")
    if score_details is None:
        normalized["score_details"] = None
    elif not isinstance(score_details, (dict, list)):
        normalized["score_details"] = {"value": score_details}

    return normalized


def write_behavioral_score(engine, row: dict[str, Any]) -> int:
    return write_behavioral_scores(engine, [row])


def write_behavioral_scores(engine, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    payload = [_normalize_score_row(row) for row in rows]
    with engine.begin() as connection:
        connection.execute(insert(behavioral_scores_table), payload)
    return len(payload)
