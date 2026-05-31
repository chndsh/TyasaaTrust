import os
import re
import sys

# Compute the absolute path to the project root directory (TyasaaTrust/)
current_dir = os.path.dirname(os.path.abspath(__file__))
is_pages_dir = os.path.basename(current_dir) == "pages"
project_root = os.path.abspath(os.path.join(current_dir, ".." if not is_pages_dir else "../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10
MERCHANT_ID_PATTERN = re.compile(r"^\d{10}$")
DEFAULT_MERCHANT_ID = "9800000000"

st.set_page_config(page_title="Tyasaa Trust", layout="wide")

# Maintained matching custom CSS rules, updated styling references for native containers
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=600;700&family=Inter:wght=400;500&display=swap');

:root {
    --bg: #121416;
    --card: #1A1D20;
    --accent: #60B224;
    --text-primary: #FFFFFF;
    --text-secondary: #A0A5AB;
    --border: #2A2F35;
}

#MainMenu, footer, header { visibility: hidden; }
.stApp { background-color: var(--bg); color: var(--text-primary); }
.block-container { padding-top: 2.5rem !important; padding-bottom: 6rem !important; max-width: 1100px !important; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: var(--text-primary); }

.brand-mark {
    text-align: center;
    margin-bottom: 0.3rem;
    letter-spacing: 0.28em;
    font-size: 0.7rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 500;
}
.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.3rem;
    font-weight: 700;
    text-align: center;
    margin: 0 0 0.4rem 0;
}
.page-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 2.2rem;
}

/* Style the native Streamlit containers to match your design requirements */
div[data-testid="stVerticalBlockBordered"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.6rem 1.8rem !important;
    box-shadow: 0 16px 30px rgba(0,0,0,0.25) !important;
}

.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.helper-text {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-top: 0.4rem;
}
.helper-text.error {
    color: #f3b9bf;
}

div[data-testid="stTextInput"] input {
    background: var(--bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(96,178,36,0.2) !important;
}

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    background: var(--accent) !important;
    color: #0d0f12 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.8rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #74c63e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 18px rgba(96,178,36,0.3) !important;
}

.metric-card {
    background: #15181b;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
.metric-label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
}
.metric-value.accent {
    color: var(--accent);
}

/* Sticky Copyright Footer Styling */
.custom-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: var(--bg);
    color: var(--text-secondary);
    text-align: center;
    padding: 1rem 0;
    font-size: 0.85rem;
    font-weight: 400;
    letter-spacing: 0.02em;
    border-top: 1px solid var(--border);
    z-index: 999;
}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)


def is_valid_merchant_id(value: str) -> bool:
    return bool(MERCHANT_ID_PATTERN.match(value or ""))


def fetch_scores(merchant_id: str) -> dict:
    response = httpx.get(f"{API_URL}/scores/{merchant_id}", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


query_merchant_id = st.query_params.get("merchant_id", "")
if "merchant_id" not in st.session_state:
    st.session_state.merchant_id = (
        query_merchant_id
        if is_valid_merchant_id(query_merchant_id)
        else DEFAULT_MERCHANT_ID
    )
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

if is_valid_merchant_id(query_merchant_id):
    st.session_state.merchant_id = query_merchant_id

st.markdown('<p class="brand-mark">Tyasaa-Trust</p>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Alternative Credit Scoring Console</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Premium trust profiling for every merchant relationship.</p>',
    unsafe_allow_html=True,
)

# Implementation of Approach A: Scoping elements into an elegant native container
with st.container(border=True):
    st.markdown('<div class="section-title">Merchant Validation</div>', unsafe_allow_html=True)
    merchant_id = st.text_input(
        "Merchant ID",
        value=st.session_state.merchant_id,
        help="Enter a 10-digit numeric Merchant ID.",
        label_visibility="collapsed"  # Hides double label since section-title is used
    )
    
    if merchant_id != st.session_state.merchant_id:
        st.session_state.merchant_id = merchant_id
        st.session_state.quiz_completed = False

    is_valid = is_valid_merchant_id(merchant_id)
    if not is_valid and merchant_id:
        st.markdown(
            '<div class="helper-text error">Merchant ID must be exactly 10 digits.</div>',
            unsafe_allow_html=True,
        )
    elif not merchant_id:
        st.markdown(
            '<div class="helper-text">Enter a 10-digit Merchant ID to unlock the psychometric assessment.</div>',
            unsafe_allow_html=True,
        )

    if is_valid:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Take Psychometric Analysis Test", use_container_width=True):
            st.session_state.quiz_completed = False
            st.session_state.quiz_merchant_id = merchant_id
            st.switch_page("pages/3_quiz.py")


if st.session_state.quiz_completed and is_valid:
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="section-title">Trust Metrics Overview</div>', unsafe_allow_html=True)
        try:
            with st.spinner("Fetching trust metrics..."):
                scores = fetch_scores(merchant_id)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Composite Trust Score</div>
                        <div class="metric-value accent">{scores.get('final_score')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Community Vouch Trust</div>
                        <div class="metric-value">{scores.get('social_score')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Digital Footprint</div>
                        <div class="metric-value">{scores.get('behavioral_score')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Psychometric Profile</div>
                        <div class="metric-value">{scores.get('psych_score')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except Exception as exc:
            st.markdown(
                f'<div class="helper-text error">Unable to fetch scores: {exc}</div>',
                unsafe_allow_html=True,
            )

# Injected persistent sticky copyright footer at the bottom layer of DOM
st.markdown(
    '<div class="custom-footer">&copy; 2026 CodeClash. All rights reserved.</div>',
    unsafe_allow_html=True
)