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
#   quiz_merchant_id     str   — merchant UUID (passed in via query param or set here)
#   quiz_state           str   — "intro" | "question" | "submitting" | "result" | "error"
#   quiz_error_msg       str   — human-readable error for the error state

import os
import time

import httpx
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL         = os.getenv("API_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10  # seconds

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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Reset Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 740px !important;
}

/* ── Page background — aged parchment with subtle grain ── */
.stApp {
    background-color: #f5ead8;
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
}

/* ── Typography base ── */
html, body, [class*="css"] {
    font-family: 'Lora', Georgia, serif !important;
    color: #1a1208;
}

/* ── Page header / brand mark ── */
.brand-mark {
    text-align: center;
    margin-bottom: 0.25rem;
    letter-spacing: 0.18em;
    font-family: 'Lora', serif;
    font-size: 0.7rem;
    color: #8b7355;
    text-transform: uppercase;
}

.page-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
    color: #1a1208;
    margin: 0 0 0.1rem 0;
    line-height: 1.2;
}

.page-subtitle {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.95rem;
    text-align: center;
    color: #6b5740;
    margin-bottom: 2rem;
}

/* ── Divider ── */
.ink-rule {
    border: none;
    border-top: 1.5px solid #c4a882;
    margin: 1.5rem auto;
    width: 80%;
}

/* ── Progress tally ── */
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
    border: 1.5px solid #c4a882;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Lora', serif;
    font-size: 0.7rem;
    color: #8b7355;
    background: transparent;
    transition: all 0.4s ease;
}
.tally-mark.done {
    background: #4a7c6f;
    border-color: #4a7c6f;
    color: #f5ead8;
}
.tally-mark.current {
    background: #c0392b;
    border-color: #c0392b;
    color: #f5ead8;
    box-shadow: 0 0 0 3px rgba(192,57,43,0.18);
}

/* ── Scenario card ── */
.scenario-card {
    background: #fdf6e8;
    border: 1px solid #d4bc96;
    border-left: 4px solid #c0392b;
    border-radius: 2px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.6rem;
    box-shadow: 3px 4px 12px rgba(26,18,8,0.08);
    animation: fadeSlideIn 0.5s ease forwards;
    position: relative;
}
.scenario-card::before {
    content: "\\201C";
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    color: #e8d5b8;
    position: absolute;
    top: -0.5rem;
    left: 0.8rem;
    line-height: 1;
}
.scenario-label {
    font-family: 'Lora', serif;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c0392b;
    margin-bottom: 0.7rem;
    font-weight: 500;
}
.scenario-text {
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    line-height: 1.75;
    color: #2c1f0e;
    font-style: italic;
}

/* ── Choice prompt ── */
.choice-prompt {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #5a3e28;
    margin-bottom: 0.9rem;
    letter-spacing: 0.02em;
}

/* ── Radio widget restyled as clickable option cards ──
   Target the outer div wrapping each radio item and make
   the entire label surface into a bordered card.           */

/* Container: stack cards vertically with no extra gap */
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.55rem !important;
}

/* Each radio item wrapper */
div[data-testid="stRadio"] > div > label {
    display: flex !important;
    align-items: flex-start !important;
    gap: 0.85rem !important;
    background: #fdf6e8 !important;
    border: 1.5px solid #d4bc96 !important;
    border-radius: 2px !important;
    padding: 0.85rem 1.1rem !important;
    cursor: pointer !important;
    transition: border-color 0.2s ease, background 0.2s ease,
                transform 0.15s ease, box-shadow 0.2s ease !important;
    animation: fadeSlideIn 0.45s ease forwards !important;
    width: 100% !important;
}

div[data-testid="stRadio"] > div > label:hover {
    border-color: #c0392b !important;
    background: #fef9f0 !important;
    transform: translateX(3px) !important;
    box-shadow: 2px 3px 8px rgba(192,57,43,0.1) !important;
}

/* Hide the native radio circle — the card border IS the selector */
div[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}

/* The text span inside the label */
div[data-testid="stRadio"] > div > label > div > p,
div[data-testid="stRadio"] > div > label p {
    font-family: 'Lora', serif !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    color: #2c1f0e !important;
    margin: 0 !important;
}

/* Selected state — vermillion left border + tinted background */
div[data-testid="stRadio"] > div > label:has(input:checked) {
    border-color: #c0392b !important;
    border-left-width: 4px !important;
    background: #fef3ee !important;
    box-shadow: 2px 3px 10px rgba(192,57,43,0.12) !important;
}

div[data-testid="stRadio"] > div > label:has(input:checked) p {
    color: #1a1208 !important;
    font-weight: 500 !important;
}

/* ── Navigation buttons ── */
.stButton > button {
    font-family: 'Lora', serif !important;
    font-size: 0.9rem !important;
    background: #1a1208 !important;
    color: #f5ead8 !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.8rem !important;
    letter-spacing: 0.08em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #c0392b !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(192,57,43,0.25) !important;
}
.stButton > button:disabled {
    background: #c4a882 !important;
    color: #f5ead8 !important;
    cursor: not-allowed !important;
}



/* ── Result page ── */
.result-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 800;
    text-align: center;
    color: #1a1208;
    margin-bottom: 0.3rem;
}
.result-score-ring {
    text-align: center;
    margin: 1.2rem 0;
}
.score-number {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 800;
    color: #1a1208;
    line-height: 1;
}
.score-denom {
    font-family: 'Lora', serif;
    font-size: 1rem;
    color: #8b7355;
}
.score-label {
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.85rem;
    color: #6b5740;
    margin-top: 0.2rem;
}
.trait-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid #e8d5b8;
}
.trait-name {
    font-family: 'Lora', serif;
    font-size: 0.9rem;
    color: #2c1f0e;
    font-weight: 500;
    text-transform: capitalize;
    min-width: 160px;
}
.trait-bar-wrap {
    flex: 1;
    height: 6px;
    background: #e8d5b8;
    border-radius: 3px;
    margin: 0 1rem;
    overflow: hidden;
}
.trait-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: #4a7c6f;
    transition: width 1s ease;
}
.trait-pct {
    font-family: 'Playfair Display', serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #1a1208;
    min-width: 38px;
    text-align: right;
}

/* ── Verdict badge ── */
.verdict-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 2px;
    font-family: 'Lora', serif;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
    margin-top: 0.4rem;
}
.verdict-high   { background:#d4edda; color:#155724; border:1px solid #b8dac0; }
.verdict-mid    { background:#fff3cd; color:#856404; border:1px solid #ffe08a; }
.verdict-low    { background:#f8d7da; color:#721c24; border:1px solid #f1aeb5; }

/* ── Intro card ── */
.intro-card {
    background: #fdf6e8;
    border: 1px solid #d4bc96;
    border-radius: 2px;
    padding: 1.6rem 1.8rem;
    margin: 1rem 0 1.5rem 0;
    box-shadow: 3px 4px 12px rgba(26,18,8,0.06);
}
.intro-card p {
    font-family: 'Lora', serif;
    font-size: 0.97rem;
    line-height: 1.75;
    color: #2c1f0e;
    margin: 0;
}

/* ── Animations ── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}

/* ── Error box ── */
.error-box {
    background: #f8d7da;
    border: 1px solid #f1aeb5;
    border-radius: 2px;
    padding: 1rem 1.2rem;
    font-family: 'Lora', serif;
    font-size: 0.92rem;
    color: #721c24;
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
    defaults = {
        "quiz_state":         "intro",
        "quiz_session_id":    None,
        "quiz_questions":     [],
        "quiz_current_index": 0,
        "quiz_answers":       {},
        "quiz_result":        None,
        "quiz_error_msg":     "",
        "quiz_merchant_id":   st.query_params.get("merchant_id", "demo-merchant-001"),
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
    st.markdown('<p class="brand-mark">TyasaaTrust · Merchant Assessment</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">व्यापारी परीक्षण</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">A psychometric assessment for Nepali merchants</p>', unsafe_allow_html=True)
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
        st.session_state.quiz_state  = "result"
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

TRAIT_DISPLAY_NAMES = {
    "integrity":            "Integrity",
    "financial_discipline": "Financial Discipline",
    "resilience":           "Resilience",
}

def _verdict(score: float) -> tuple[str, str]:
    """Return (label, css_class) based on composite score."""
    if score >= 0.70:
        return "Strong Trust Profile",  "verdict-high"
    if score >= 0.45:
        return "Developing Trust Profile", "verdict-mid"
    return "Needs Improvement", "verdict-low"


def render_result() -> None:
    render_header()

    result      = st.session_state.quiz_result
    psych_score = result["psych_score"]
    breakdown   = result["breakdown"]

    score_pct   = round(psych_score * 100, 1)
    verdict_lbl, verdict_cls = _verdict(psych_score)

    # ── Score ring ──
    st.markdown(
        f"""
        <div class="result-score-ring">
            <p class="result-header">Assessment Complete</p>
            <div style="margin:1rem 0;">
                <span class="score-number">{score_pct}</span>
                <span class="score-denom"> / 100</span>
            </div>
            <div>
                <span class="verdict-badge {verdict_cls}">{verdict_lbl}</span>
            </div>
            <p class="score-label" style="margin-top:0.6rem;">
                Psychometric Trust Score
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="ink-rule"/>', unsafe_allow_html=True)

    # ── Trait breakdown ──
    st.markdown(
        '<p style="font-family:\'Playfair Display\',serif; font-weight:600; '
        'font-size:0.95rem; color:#5a3e28; margin-bottom:0.4rem; '
        'letter-spacing:0.04em;">Trait Breakdown</p>',
        unsafe_allow_html=True,
    )

    for trait_key, bd in breakdown.items():
        display_name = TRAIT_DISPLAY_NAMES.get(trait_key, trait_key.replace("_", " ").title())
        pct          = round(bd["normalized"] * 100)
        bar_color    = (
            "#4a7c6f" if pct >= 70
            else "#c0392b" if pct < 45
            else "#c49a3c"
        )

        st.markdown(
            f"""
            <div class="trait-row">
                <span class="trait-name">{display_name}</span>
                <div class="trait-bar-wrap">
                    <div class="trait-bar-fill"
                         style="width:{pct}%; background:{bar_color};"></div>
                </div>
                <span class="trait-pct">{pct}%</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="ink-rule"/>', unsafe_allow_html=True)

    # ── Session metadata (useful for judges / debugging) ──
    with st.expander("Session details", expanded=False):
        st.markdown(
            f"""
            <div style="font-family:'Lora',serif; font-size:0.82rem;
                        color:#6b5740; line-height:1.8;">
                <strong>Session ID:</strong> {result['session_id']}<br/>
                <strong>Merchant ID:</strong> {result['merchant_id']}<br/>
                <strong>Scored at:</strong> {result['scored_at']}<br/>
                <strong>Raw psych_score:</strong> {result['psych_score']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Retake / home buttons ──
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Retake Assessment", use_container_width=True):
            _reset_quiz()
    with col3:
        if st.button("← Dashboard", use_container_width=True):
            st.switch_page("pages/4_dashboard.py")


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
    "result":      render_result,
    "error":       render_error,
}

current_state = st.session_state.get("quiz_state", "intro")
renderer      = STATE_RENDERERS.get(current_state, render_intro)
renderer()