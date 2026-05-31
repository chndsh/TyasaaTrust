# frontend/pages/3_quiz.py
# TyasaaTrust — Psychometric Assessment
# Visual Novel / Narrative Interface
#
# Session state keys used on this page:
#   quiz_session_id      str   — UUID from the backend
#   quiz_questions       list  — the 5 SafeQuestion dicts
#   quiz_current_index   int   — which question we are on (0–4)
#   quiz_answers         dict  — {question_id: option_id} accumulated answers
#   quiz_result          dict  — ScoreResult returned after submission
#   quiz_merchant_id     str   — 10-digit merchant ID (passed in via query param or set here)
#   quiz_state           str   — "intro" | "question" | "submitting" | "complete" | "error"
#   quiz_error_msg       str   — human-readable error for the error state

import os
import sys

# Compute the absolute path to the project root directory (TyasaaTrust/)
# Assumes the file is located inside frontend/ or frontend/pages/
current_dir = os.path.dirname(os.path.abspath(__file__))
is_pages_dir = os.path.basename(current_dir) == "pages"
project_root = os.path.abspath(os.path.join(current_dir, ".." if not is_pages_dir else "../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import re

import httpx
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL         = os.getenv("API_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10  # seconds
MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")
DEFAULT_MERCHANT_ID = "9800000000"

st.set_page_config(
    page_title="Trust Assessment — TyasaaTrust",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Visual Design — injected CSS
#
# Aesthetic: Worn Manuscript meets Mountain Trading Post
# Palette:   Deep ink (#1a1208) on aged parchment (#f5ead8)
#            Accent: temple vermillion (#c0392b)
#            Muted:  weathered teal (#4a7c6f)
# Fonts:     Playfair Display (scenario headlines) +
#            Lora (body / option text) — both from Google Fonts
# ---------------------------------------------------------------------------

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&family=Inter:wght@400;500&display=swap');

:root {
    --bg: #121416;
    --card: #1A1D20;
    --accent: #60B224;
    --text-primary: #FFFFFF;
    --text-secondary: #A0A5AB;
    --border: #2A2F35;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 840px !important;
}

.stApp {
    background-color: var(--bg);
    color: var(--text-primary);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

.brand-mark {
    text-align: center;
    margin-bottom: 0.25rem;
    letter-spacing: 0.28em;
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 500;
}

.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin: 0 0 0.2rem 0;
}

.page-subtitle {
    font-size: 0.95rem;
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 1.8rem;
}

.ink-rule {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.3rem auto 1.8rem;
    width: 80%;
}

.tally-bar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 1.2rem 0 1.8rem 0;
}
.tally-mark {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: var(--text-secondary);
    background: transparent;
    transition: all 0.4s ease;
}
.tally-mark.done {
    background: var(--accent);
    border-color: var(--accent);
    color: #0d0f12;
}
.tally-mark.current {
    background: #0d0f12;
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 0 0 3px rgba(96,178,36,0.15);
}

.scenario-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.6rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    animation: fadeSlideIn 0.5s ease forwards;
}

.scenario-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.7rem;
    font-weight: 500;
}

.scenario-text {
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text-primary);
}

.choice-prompt {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.9rem;
    letter-spacing: 0.02em;
}

div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.55rem !important;
}

div[data-testid="stRadio"] > div > label {
    display: flex !important;
    align-items: flex-start !important;
    gap: 0.85rem !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.1rem !important;
    cursor: pointer !important;
    transition: border-color 0.2s ease, background 0.2s ease,
                transform 0.15s ease, box-shadow 0.2s ease !important;
    animation: fadeSlideIn 0.45s ease forwards !important;
    width: 100% !important;
}

div[data-testid="stRadio"] > div > label:hover {
    border-color: var(--accent) !important;
    background: #1f2428 !important;
    transform: translateX(3px) !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.2) !important;
}

div[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}

div[data-testid="stRadio"] > div > label > div > p,
div[data-testid="stRadio"] > div > label p {
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
}

div[data-testid="stRadio"] > div > label:has(input:checked) {
    border-color: var(--accent) !important;
    background: #1f2420 !important;
    box-shadow: 0 6px 18px rgba(96,178,36,0.15) !important;
}

div[data-testid="stRadio"] > div > label:has(input:checked) p {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

div[data-testid="stTextInput"] input {
    background: var(--card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(96,178,36,0.2) !important;
}

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    background: var(--accent) !important;
    color: #0d0f12 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.8rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #74c63e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 18px rgba(96,178,36,0.3) !important;
}
.stButton > button:disabled {
    background: #2d3438 !important;
    color: var(--text-secondary) !important;
    cursor: not-allowed !important;
}

.result-header {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    text-align: center;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}
.result-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.95rem;
}

.intro-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.6rem 1.8rem;
    margin: 1rem 0 1.5rem 0;
    box-shadow: 0 12px 24px rgba(0,0,0,0.2);
}
.intro-card p {
    font-size: 0.97rem;
    line-height: 1.7;
    color: var(--text-primary);
    margin: 0;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}

.error-box {
    background: #2a1518;
    border: 1px solid #5f2b2f;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.92rem;
    color: #f3b9bf;
    margin: 1rem 0;
}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_start_session(merchant_id: str) -> dict:
    resp = httpx.post(
        f"{API_URL}/psych/session/start",
        json={"merchant_id": merchant_id},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def api_submit_answers(session_id: str, answers: dict[str, str]) -> dict:
    resp = httpx.post(
        f"{API_URL}/psych/session/{session_id}/submit",
        json={"answers": answers},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state() -> None:
    seed_merchant_id = st.session_state.get("merchant_id")
    if not seed_merchant_id or not MERCHANT_ID_PATTERN.match(seed_merchant_id):
        query_merchant_id = st.query_params.get("merchant_id", "")
        seed_merchant_id = (
            query_merchant_id
            if MERCHANT_ID_PATTERN.match(query_merchant_id)
            else DEFAULT_MERCHANT_ID
        )
    defaults = {
        "quiz_state":         "intro",
        "quiz_session_id":    None,
        "quiz_questions":     [],
        "quiz_current_index": 0,
        "quiz_answers":       {},
        "quiz_result":        None,
        "quiz_error_msg":     "",
        "quiz_merchant_id":   seed_merchant_id,
        "quiz_selected":      None,   # holds radio selection for current question
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

# ---------------------------------------------------------------------------
# Shared header — rendered on every state
# ---------------------------------------------------------------------------

def render_header() -> None:
    st.markdown('<p class="brand-mark">TyasaaTrust · Psychometric Analysis</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Psychometric Trust Assessment</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Complete the five-question assessment to unlock your trust profile.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="ink-rule"/>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Progress tally
# ---------------------------------------------------------------------------

def render_tally(current: int, total: int = 5) -> None:
    marks = ""
    for i in range(total):
        if i < current:
            marks += f'<div class="tally-mark done">✓</div>'
        elif i == current:
            marks += f'<div class="tally-mark current">{i + 1}</div>'
        else:
            marks += f'<div class="tally-mark">{i + 1}</div>'
    st.markdown(
        f'<div class="tally-bar">{marks}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# State: INTRO
# ---------------------------------------------------------------------------

def render_intro() -> None:
    render_header()

    st.markdown("""
    <div class="intro-card">
    <p>
    You will be presented with <strong>five real-life business scenarios</strong>
    drawn from the daily experience of Nepali merchants — covering Udharo credit,
    festive season planning, supplier relationships, setbacks, and growth decisions.
    </p>
    <br/>
    <p>
    For each scenario, choose the response that most honestly reflects how
    <em>you</em> would act. There are no trick questions.
    Your answers generate a psychometric trust profile used only within TyasaaTrust.
    </p>
    <br/>
    <p>
    The assessment takes approximately <strong>three to five minutes</strong>.
    </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Begin Assessment →", use_container_width=True):
            _start_session()


def _start_session() -> None:
    merchant_id = st.session_state.quiz_merchant_id
    if not MERCHANT_ID_PATTERN.match(merchant_id):
        st.session_state.quiz_error_msg = (
            "Merchant ID must be a 10-digit numeric value. "
            "Please return to the landing page and correct it."
        )
        st.session_state.quiz_state = "error"
        st.rerun()
    try:
        with st.spinner("Preparing your assessment…"):
            data = api_start_session(merchant_id)
        st.session_state.quiz_session_id    = data["session_id"]
        st.session_state.quiz_questions     = data["questions"]
        st.session_state.quiz_current_index = 0
        st.session_state.quiz_answers       = {}
        st.session_state.quiz_selected      = None
        st.session_state.quiz_state         = "question"
        st.rerun()
    except httpx.HTTPStatusError as e:
        st.session_state.quiz_error_msg = (
            f"The server returned an error ({e.response.status_code}). "
            "Please ensure the backend is running and try again."
        )
        st.session_state.quiz_state = "error"
        st.rerun()
    except Exception as e:
        st.session_state.quiz_error_msg = (
            f"Could not reach the backend at {API_URL}. "
            f"Details: {e}"
        )
        st.session_state.quiz_state = "error"
        st.rerun()


# ---------------------------------------------------------------------------
# State: QUESTION
# ---------------------------------------------------------------------------

def render_question() -> None:
    render_header()

    questions   = st.session_state.quiz_questions
    idx         = st.session_state.quiz_current_index
    question    = questions[idx]
    total       = len(questions)

    render_tally(current=idx, total=total)

    # ── Scenario card ──
    st.markdown(
        f"""
        <div class="scenario-card">
            <div class="scenario-label">Scenario {idx + 1} of {total}</div>
            <div class="scenario-text">{question['scenario']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Choice prompt ──
    st.markdown(
        '<p class="choice-prompt">What would you do?</p>',
        unsafe_allow_html=True,
    )

    # ── Option radio cards ──
    # Each label is styled by CSS into a full-width clickable card.
    # The native radio circle is hidden via CSS — clicking anywhere
    # on the card surface triggers selection. The option letter (A/B/C/D)
    # is prepended to the label text so it appears bold in the card.
    # Parsing chosen_id just splits on the first "  —  " separator.

    radio_options = [
        f"**{opt['id']}**  —  {opt['text']}"
        for opt in question["options"]
    ]
    raw_key = f"radio_q_{question['id']}"

    chosen_label = st.radio(
        "Select your response:",
        options=radio_options,
        index=None,
        key=raw_key,
        label_visibility="collapsed",
    )

    # Parse option ID from the selected label (strip markdown bold markers)
    if chosen_label:
        raw_id = chosen_label.split("  —  ")[0].replace("**", "").strip()
    else:
        raw_id = None
    chosen_id = raw_id
    st.session_state.quiz_selected = chosen_id

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Navigation ──
    col_back, col_spacer, col_next = st.columns([1, 2, 1])

    with col_back:
        if idx > 0:
            if st.button("← Back", use_container_width=True):
                # Remove previous answer so it can be changed
                prev_q_id = questions[idx - 1]["id"]
                st.session_state.quiz_answers.pop(prev_q_id, None)
                st.session_state.quiz_current_index -= 1
                st.session_state.quiz_selected = None
                st.rerun()

    with col_next:
        is_last    = (idx == total - 1)
        btn_label  = "Submit →" if is_last else "Next →"
        btn_active = chosen_id is not None

        if st.button(btn_label, disabled=not btn_active, use_container_width=True):
            # Record this answer
            st.session_state.quiz_answers[question["id"]] = chosen_id

            if is_last:
                st.session_state.quiz_state = "submitting"
                st.rerun()
            else:
                st.session_state.quiz_current_index += 1
                st.session_state.quiz_selected = None
                st.rerun()


# ---------------------------------------------------------------------------
# State: SUBMITTING
# ---------------------------------------------------------------------------

def render_submitting() -> None:
    render_header()
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 0;">
            <p style="font-family:'Playfair Display',serif; font-size:1.3rem;
                      color:#1a1208; font-style:italic;">
                Calculating your trust profile…
            </p>
            <p style="font-family:'Lora',serif; font-size:0.85rem; color:#8b7355;">
                Applying the psychometric model to your responses.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    session_id = st.session_state.quiz_session_id
    answers    = st.session_state.quiz_answers

    try:
        result = api_submit_answers(session_id, answers)
        st.session_state.quiz_result = result
        st.session_state.quiz_state  = "complete"
        st.session_state.quiz_completed = True
        st.session_state.merchant_id = result.get("merchant_id")
        st.rerun()
    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", str(e))
        st.session_state.quiz_error_msg = f"Submission failed: {detail}"
        st.session_state.quiz_state     = "error"
        st.rerun()
    except Exception as e:
        st.session_state.quiz_error_msg = (
            f"Could not reach the backend at {API_URL}. Details: {e}"
        )
        st.session_state.quiz_state = "error"
        st.rerun()


# ---------------------------------------------------------------------------
# State: RESULT
# ---------------------------------------------------------------------------

def render_complete() -> None:
    render_header()

    st.markdown(
        """
        <div class="intro-card">
            <p class="result-header">Thank you for completing the assessment.</p>
            <p class="result-subtitle">Your responses are saved. Redirecting you to the main console…</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.2)
    st.switch_page("app.py")


def _reset_quiz() -> None:
    keys_to_clear = [
        "quiz_state", "quiz_session_id", "quiz_questions",
        "quiz_current_index", "quiz_answers", "quiz_result",
        "quiz_error_msg", "quiz_selected",
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


# ---------------------------------------------------------------------------
# State: ERROR
# ---------------------------------------------------------------------------

def render_error() -> None:
    render_header()
    st.markdown(
        f"""
        <div class="error-box">
            <strong>Something went wrong.</strong><br/>
            {st.session_state.quiz_error_msg}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Try Again"):
        _reset_quiz()


# ---------------------------------------------------------------------------
# Router — dispatch to the correct state renderer
# ---------------------------------------------------------------------------

STATE_RENDERERS = {
    "intro":       render_intro,
    "question":    render_question,
    "submitting":  render_submitting,
    "complete":    render_complete,
    "error":       render_error,
}

current_state = st.session_state.get("quiz_state", "intro")
renderer      = STATE_RENDERERS.get(current_state, render_intro)
renderer()