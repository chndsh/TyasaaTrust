# backend/routers/psych.py
# TyasaaTrust — Psychometric Quiz Router
#
# Endpoints:
#   POST   /psych/session/start                — create session, return questions
#   GET    /psych/session/{session_id}          — retrieve session status
#   POST   /psych/session/{session_id}/submit   — submit answers, return score
#
# Design contract:
#   - This router is a pure HTTP adapter. Zero business logic lives here.
#   - All scoring and session logic is delegated to psychometric.py.
#   - Option weight vectors are stripped before questions reach the client.
#   - Errors from the module are mapped to precise HTTP status codes.

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from backend.modules.psychometric import (
    ScoreResult,
    SessionState,
    create_session,
    get_session,
    score_session,
)

router = APIRouter(tags=["Psychometric"])
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


# ---------------------------------------------------------------------------
# Pydantic request / response models
#
# Keeping request and response models in the same file as the router that
# uses them avoids premature abstraction for a project of this scope.
# ---------------------------------------------------------------------------

# --- Request bodies ----------------------------------------------------------

class StartSessionRequest(BaseModel):
    merchant_id: MerchantId


class SubmitAnswersRequest(BaseModel):
    answers: dict[str, str] = Field(
        ...,
        description=(
            "Mapping of question_id to chosen option_id. "
            "Must contain exactly one entry per question in the session."
        ),
        examples=[{"Q03": "B", "Q07": "A", "Q11": "C", "Q14": "B", "Q18": "D"}],
    )

    @field_validator("answers")
    @classmethod
    def answers_must_not_be_empty(cls, v: dict[str, str]) -> dict[str, str]:
        if not v:
            raise ValueError("Answers dict must not be empty.")
        return v


# --- Response bodies ---------------------------------------------------------

class SafeOption(BaseModel):
    """Option shape sent to the client — weight vector deliberately excluded."""
    id:   str
    text: str


class SafeQuestion(BaseModel):
    """Question shape sent to the client — weights stripped from every option."""
    id:       str
    scenario: str
    options:  list[SafeOption]


class StartSessionResponse(BaseModel):
    session_id:  str
    merchant_id: MerchantId
    created_at:  str
    questions:   list[SafeQuestion]


class SessionStatusResponse(BaseModel):
    session_id:  str
    merchant_id: MerchantId
    created_at:  str
    submitted:   bool
    question_ids: list[str]


class TraitBreakdownResponse(BaseModel):
    raw:        int
    max:        int
    normalized: int
    weighted:   int


class ScoreResponse(BaseModel):
    session_id:  str
    merchant_id: MerchantId
    psych_score: int
    breakdown:   dict[str, TraitBreakdownResponse]
    answers:     dict[str, str]
    scored_at:   str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_weights(state: SessionState) -> list[SafeQuestion]:
    """
    Return the session's questions with option weight vectors removed.

    This is the single enforcement point ensuring weights never leave
    the server boundary — called by every endpoint that returns questions.
    """
    return [
        SafeQuestion(
            id=q["id"],
            scenario=q["scenario"],
            options=[
                SafeOption(id=opt["id"], text=opt["text"])
                for opt in q["options"]
            ],
        )
        for q in state["questions"]
    ]


def _map_module_error(exc: Exception) -> HTTPException:
    """
    Translate module-layer exceptions into appropriate HTTP responses.

    KeyError  → 404 (session not found / expired)
    ValueError → 422 (bad client input — missing answers, invalid options, etc.)
    Any other  → 500 (unexpected server fault)
    """
    if isinstance(exc, KeyError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred. Please try again.",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/session/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new psychometric assessment session",
    description=(
        "Creates a new session for the given merchant. "
        "Returns a session_id and exactly 5 questions selected via "
        "stratified cluster sampling. Option weights are never included "
        "in the response."
    ),
)
def start_session(body: StartSessionRequest) -> StartSessionResponse:
    """
    POST /psych/session/start

    Request body:  { "merchant_id": "<10-digit ID>" }
    Response:      session_id, created_at, 5 stripped questions
    """
    try:
        state = create_session(merchant_id=body.merchant_id)
    except Exception as exc:
        raise _map_module_error(exc) from exc

    return StartSessionResponse(
        session_id=state["session_id"],
        merchant_id=state["merchant_id"],
        created_at=state["created_at"],
        questions=_strip_weights(state),
    )


@router.get(
    "/session/{session_id}",
    response_model=SessionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve the status of an active session",
    description=(
        "Returns metadata for an existing session: its IDs, timestamps, "
        "and whether it has already been submitted. "
        "Does not return question text or answers."
    ),
)
def retrieve_session(session_id: str) -> SessionStatusResponse:
    """
    GET /psych/session/{session_id}

    Used by the frontend to check session state on page reload,
    and by Person C's fusion module to verify a session exists
    before requesting a score.
    """
    try:
        state = get_session(session_id=session_id)
    except Exception as exc:
        raise _map_module_error(exc) from exc

    return SessionStatusResponse(
        session_id=state["session_id"],
        merchant_id=state["merchant_id"],
        created_at=state["created_at"],
        submitted=state["submitted"],
        question_ids=state["question_ids"],
    )


@router.post(
    "/session/{session_id}/submit",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answers and receive the psychometric score",
    description=(
        "Accepts the merchant's answers and runs the Weighted Additive Model "
        "scoring algorithm. Returns the composite psych_score in [0, 1000] "
        "and a full per-trait breakdown. Each session may only be submitted once."
    ),
)
def submit_answers(
    session_id: str,
    body: SubmitAnswersRequest,
) -> ScoreResponse:
    """
    POST /psych/session/{session_id}/submit

    Request body:  { "answers": { "<question_id>": "<option_id>", ... } }
    Response:      psych_score, per-trait breakdown, echoed answers, timestamp

    The psych_score integer is the value Person C's fusion.py should consume
    when computing the final trust score for this merchant.
    """
    try:
        result: ScoreResult = score_session(
            session_id=session_id,
            answers=body.answers,
        )
    except Exception as exc:
        raise _map_module_error(exc) from exc

    return ScoreResponse(
        session_id=result["session_id"],
        merchant_id=result["merchant_id"],
        psych_score=result["psych_score"],
        breakdown={
            trait: TraitBreakdownResponse(**bd)
            for trait, bd in result["breakdown"].items()
        },
        answers=result["answers"],
        scored_at=result["scored_at"],
    )