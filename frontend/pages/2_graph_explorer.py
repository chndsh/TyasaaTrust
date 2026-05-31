import os
import re
import sys

# Compute the absolute path to the project root directory (TyasaaTrust/)
# Assumes the file is located inside frontend/ or frontend/pages/
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

st.set_page_config(page_title="Social Graph Explorer", layout="wide")

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
/* Expanded bottom padding to ensure contents don't get clipped behind the fixed footer */
.block-container { padding-top: 2.5rem !important; padding-bottom: 6rem !important; max-width: 1100px !important; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: var(--text-primary); }

/* Targets and customizes Streamlit's native container wrapper */
div[data-testid="stVerticalBlockBordered"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 16px 30px rgba(0,0,0,0.25) !important;
}

.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
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
    background: var(--accent) !important;
    color: #0d0f12 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover:not(:disabled) {
    background: #74c63e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 18px rgba(96,178,36,0.3) !important;
}
.stButton > button:disabled {
    background: #2d3438 !important;
    color: var(--text-secondary) !important;
    cursor: not-allowed !important;
}

.helper-text {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-top: 0.4rem;
}
.helper-text.error {
    color: #f3b9bf;
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

st.title("Social Graph Explorer")

# Replaced dangerous raw HTML strings with an explicitly bounded Streamlit native block
with st.container(border=True):
    st.markdown('<div class="section-title">Community Vouch Trust</div>', unsafe_allow_html=True)
    
    merchant_id = st.text_input(
        "Merchant ID", 
        value=DEFAULT_MERCHANT_ID,
        label_visibility="collapsed"  # Collapsed to prevent duplicating the layout header
    )
    
    is_valid = bool(MERCHANT_ID_PATTERN.match(merchant_id or ""))
    
    if not is_valid and merchant_id:
        st.markdown(
            '<div class="helper-text error">Merchant ID must be exactly 10 digits.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    
    if st.button("Fetch social score", disabled=not is_valid, use_container_width=True):
        with st.spinner("Loading social graph score..."):
            try:
                response = httpx.get(f"{API_URL}/graph/{merchant_id}", timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                st.json(response.json())
            except Exception as exc:
                st.error(f"Unable to reach backend: {exc}")

# Injected persistent sticky copyright footer at the bottom layer of DOM
st.markdown(
    '<div class="custom-footer">&copy; 2026 CodeClash. All rights reserved.</div>',
    unsafe_allow_html=True
)