# backend/modules/psychometric.py
# TyasaaTrust — Psychometric Engine (Redis-backed sessions)
#
# Responsibilities:
#   1. Stratified session sampling  — one question per cluster, 5 total
#   2. Session state management     — Redis-backed, TTL-expiring
#   3. Scoring algorithm            — Weighted Additive Model (WAM)
#   4. Result schema construction   — clean typed dict for the router
#
# This module has zero FastAPI imports. It is pure Python and fully
# unit-testable in isolation.
#
# Redis key convention:
#   psych:session:{session_id}  →  JSON-serialised SessionState string
#   TTL: SESSION_TTL_SECONDS (default 3600)

from __future__ import annotations

import json
import os
import random
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import TypedDict, Any

import redis
from backend.data.questions import QUESTION_BANK

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRAIT_WEIGHTS: dict[str, float] = {
    "integrity":            0.35,
    "financial_discipline": 0.35,
    "resilience":           0.30,
}

QUESTIONS_PER_SESSION:      int = 5
MAX_POINTS_PER_TRAIT_PER_Q: int = 4
MAX_RAW_PER_TRAIT:          int = MAX_POINTS_PER_TRAIT_PER_Q * QUESTIONS_PER_SESSION  # 20
SCORE_SCALE:                int = 1000

SESSION_TTL_SECONDS: int = int(os.getenv("PSYCH_SESSION_TTL", "3600"))
REDIS_KEY_PREFIX:    str = "psych:session:"
LATEST_SCORE_KEY_PREFIX: str = "psych:latest:"
MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")


def _validate_merchant_id(merchant_id: str) -> None:
    if not MERCHANT_ID_PATTERN.match(merchant_id):
        raise ValueError("merchant_id must be a 10-digit numeric string.")

# ---------------------------------------------------------------------------
# Redis connection
#
# Uses environment variables so the same code works locally (localhost)
# and inside Docker Compose (service name "redis").
# Connection pooling is handled by redis-py automatically.
# ---------------------------------------------------------------------------

def _get_redis() -> redis.Redis:
    """
    Return a Redis client instance.

    Reads REDIS_HOST and REDIS_PORT from the environment, falling back to
    sensible defaults that match the docker-compose.yml service definition.

    decode_responses=True means all Redis values come back as Python strings
    rather than bytes — we are storing JSON so this is always correct.
    """
    try:
        import redis
    except Exception as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError("redis is required for psychometric session storage") from exc

    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
    )


# ---------------------------------------------------------------------------
# Typed schemas
# ---------------------------------------------------------------------------

class OptionSchema(TypedDict):
    id:      str
    text:    str
    weights: dict[str, int]


class QuestionSchema(TypedDict):
    id:       str
    cluster:  str
    scenario: str
    options:  list[OptionSchema]


class SessionState(TypedDict):
    session_id:   str
    merchant_id:  str
    questions:    list[QuestionSchema]
    question_ids: list[str]
    created_at:   str
    submitted:    bool


class TraitBreakdown(TypedDict):
    raw:        int
    max:        int
    normalized: int
    weighted:   int


class ScoreResult(TypedDict):
    session_id:  str
    merchant_id: str
    psych_score: int
    breakdown:   dict[str, TraitBreakdown]
    answers:     dict[str, str]
    scored_at:   str


# ---------------------------------------------------------------------------
# Redis helpers — serialization boundary
#
# Everything above this line is pure Python dicts and logic.
# Everything below this line touches Redis.
# The two layers never mix — callers always deal with typed Python objects.
# ---------------------------------------------------------------------------

def _redis_key(session_id: str) -> str:
    return f"{REDIS_KEY_PREFIX}{session_id}"


def _latest_score_key(merchant_id: str) -> str:
    return f"{LATEST_SCORE_KEY_PREFIX}{merchant_id}"


def _write_session(state: SessionState, ttl: int = SESSION_TTL_SECONDS) -> None:
    """
    Persist a SessionState to Redis as a JSON string with a TTL.

    The entire state is serialised as one atomic SET so there is no
    partial-write risk — a session either exists completely or not at all.
    """
    client = _get_redis()
    client.setex(
        name=_redis_key(state["session_id"]),
        time=ttl,
        value=json.dumps(state),
    )


def _write_latest_score(
    merchant_id: str,
    psych_score: int,
    scored_at: str,
    ttl: int = SESSION_TTL_SECONDS,
) -> None:
    client = _get_redis()
    payload = {
        "merchant_id": merchant_id,
        "psych_score": psych_score,
        "scored_at": scored_at,
        "status": "stored",
    }
    client.setex(
        name=_latest_score_key(merchant_id),
        time=ttl,
        value=json.dumps(payload),
    )


def _read_session(session_id: str) -> SessionState:
    """
    Retrieve and deserialise a SessionState from Redis.

    Raises
    ------
    KeyError
        If the session does not exist or has expired.
    """
    client  = _get_redis()
    raw     = client.get(_redis_key(session_id))

    if raw is None:
        raise KeyError(
            f"Session '{session_id}' does not exist or has expired. "
            "Please start a new session."
        )

    return json.loads(raw)


def _delete_session(session_id: str) -> None:
    """Remove a session from Redis after scoring (optional cleanup)."""
    _get_redis().delete(_redis_key(session_id))


# ---------------------------------------------------------------------------
# Internal sampling logic
# ---------------------------------------------------------------------------

def _group_by_cluster(
    bank: list[QuestionSchema],
) -> dict[str, list[QuestionSchema]]:
    """Partition the full question bank into per-cluster buckets."""
    buckets: dict[str, list[QuestionSchema]] = defaultdict(list)
    for question in bank:
        buckets[question["cluster"]].append(question)
    return dict(buckets)


def _sample_questions(bank: list[QuestionSchema]) -> list[QuestionSchema]:
    """
    Stratified sampling: select exactly one question from each cluster.

    Raises
    ------
    ValueError
        If the bank is missing one or more of the five expected clusters.
    """
    buckets           = _group_by_cluster(bank)
    expected_clusters = {"C1", "C2", "C3", "C4", "C5"}

    missing = expected_clusters - buckets.keys()
    if missing:
        raise ValueError(
            f"Question bank is missing clusters: {missing}. "
            "Cannot build a valid session."
        )

    sampled: list[QuestionSchema] = [
        random.choice(buckets[cluster_id])
        for cluster_id in sorted(expected_clusters)
    ]
    random.shuffle(sampled)
    return sampled


def _resolve_option(question: QuestionSchema, chosen_id: str) -> OptionSchema:
    """
    Return the OptionSchema for a given option id within a question.

    Raises
    ------
    ValueError
        If chosen_id is not among the question's valid option ids.
    """
    for option in question["options"]:
        if option["id"] == chosen_id:
            return option

    valid = [o["id"] for o in question["options"]]
    raise ValueError(
        f"Option '{chosen_id}' is not valid for question '{question['id']}'. "
        f"Expected one of: {valid}"
    )


# ---------------------------------------------------------------------------
# Public API — the only surface the FastAPI router touches
# ---------------------------------------------------------------------------

def create_session(merchant_id: str) -> SessionState:
    """
    Initialise and persist a new psychometric session for a merchant.

    Samples 5 questions via stratified cluster sampling, writes the full
    session state to Redis with a TTL, and returns the SessionState.

    Note
    ----
    The router is responsible for stripping option weight vectors before
    sending questions to the client. Weights must never be exposed over HTTP.
    """
    _validate_merchant_id(merchant_id)
    session_id = str(uuid.uuid4())
    questions  = _sample_questions(QUESTION_BANK)

    state: SessionState = {
        "session_id":   session_id,
        "merchant_id":  merchant_id,
        "questions":    questions,
        "question_ids": [q["id"] for q in questions],
        "created_at":   datetime.now(timezone.utc).isoformat(),
        "submitted":    False,
    }

    _write_session(state)
    return state


def get_psychometric_score(merchant_id: str) -> dict[str, int | str]:
    """
    Retrieve the latest psychometric score for a merchant.

    Returns a stubbed score if no completed session has been stored yet.
    """
    _validate_merchant_id(merchant_id)
    client = _get_redis()
    raw = client.get(_latest_score_key(merchant_id))
    if raw is None:
        return {
            "merchant_id": merchant_id,
            "psych_score": 620,
            "status": "stub",
        }
    return json.loads(raw)


def get_session(session_id: str) -> SessionState:
    """
    Retrieve an active session by its UUID.

    Raises
    ------
    KeyError
        If the session does not exist or has expired in Redis.
    """
    return _read_session(session_id)


def score_session(
    session_id: str,
    answers: dict[str, str],
) -> ScoreResult:
    """
    Score a completed session against the merchant's submitted answers.

    Parameters
    ----------
    session_id:
        UUID string identifying the active session in Redis.
    answers:
        {question_id: chosen_option_id} — must be complete and exact.

    Returns
    -------
    ScoreResult
        Composite psych_score in [0, 1000], per-trait breakdown,
        echoed answers, and a UTC timestamp.

    Raises
    ------
    KeyError
        Session not found or expired.
    ValueError
        Answers incomplete, contain unknown question IDs, reference
        invalid option IDs, or session was already submitted.
    """
    state = _read_session(session_id)

    # --- Idempotency guard ---------------------------------------------------
    if state["submitted"]:
        raise ValueError(
            f"Session '{session_id}' has already been scored. "
            "Each session may only be submitted once."
        )

    # --- Validate answer completeness ----------------------------------------
    expected_ids = set(state["question_ids"])
    received_ids = set(answers.keys())

    missing  = expected_ids - received_ids
    spurious = received_ids - expected_ids

    if missing:
        raise ValueError(
            f"Incomplete submission. Missing answers for: {missing}"
        )
    if spurious:
        raise ValueError(
            f"Answers submitted for unrecognised question IDs: {spurious}"
        )

    # --- Accumulate raw trait points -----------------------------------------
    raw_scores: dict[str, int]    = {trait: 0 for trait in TRAIT_WEIGHTS}
    question_map: dict[str, QuestionSchema] = {
        q["id"]: q for q in state["questions"]
    }

    for question_id, chosen_option_id in answers.items():
        question = question_map[question_id]
        option   = _resolve_option(question, chosen_option_id)
        for trait, points in option["weights"].items():
            raw_scores[trait] += points

    # --- Build per-trait breakdown --------------------------------------------
    breakdown: dict[str, TraitBreakdown] = {}
    for trait, raw in raw_scores.items():
        normalized = int(round((raw / MAX_RAW_PER_TRAIT) * SCORE_SCALE))
        weighted   = int(round(normalized * TRAIT_WEIGHTS[trait]))
        breakdown[trait] = {
            "raw":        normalized,
            "max":        SCORE_SCALE,
            "normalized": normalized,
            "weighted":   weighted,
        }

    # --- Composite score -----------------------------------------------------
    psych_score = int(round(sum(t["weighted"] for t in breakdown.values())))
    psych_score = max(0, min(psych_score, SCORE_SCALE))

    # --- Mark submitted and persist back to Redis ----------------------------
    # We update rather than delete so the record survives for audit/debugging
    # during the hackathon demo window. In production, delete after scoring.
    state["submitted"] = True
    _write_session(state, ttl=SESSION_TTL_SECONDS)

    scored_at = datetime.now(timezone.utc).isoformat()
    _write_latest_score(state["merchant_id"], psych_score, scored_at)

    return {
        "session_id":  session_id,
        "merchant_id": state["merchant_id"],
        "psych_score": psych_score,
        "breakdown":   breakdown,
        "answers":     answers,
        "scored_at":   datetime.now(timezone.utc).isoformat(),
    }


def score_responses(responses: list[dict]) -> dict:
    """Compatibility shim used by the simple psych router.

    This is a lightweight scoring fallback for environments running the
    demo without Redis-backed sessions. It returns a small result dict
    similar to the legacy implementation used by the routers.
    """
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
    """Return a stubbed psychometric profile for a merchant.

    This keeps the scoring pipeline working in demo/test environments
    when a persistent psychometric store is not available.
    """
    return {
        "merchant_id": merchant_id,
        "psych_score": 0.57,
        "traits": {"openness": 0.6, "conscientiousness": 0.55},
        "status": "stub",
    }