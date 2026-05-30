import os
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

st.title("Trust Score Dashboard")
merchant_id = st.text_input("Merchant ID", value="merchant-demo")

if st.button("Refresh scores"):
    with st.spinner("Fetching scores..."):
        try:
            response = httpx.get(f"{API_URL}/scores/{merchant_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            st.metric("Final score", data.get("final_score"))
            st.metric("Social score", data.get("social_score"))
            st.metric("Psych score", data.get("psych_score"))
            st.metric("Behavioral score", data.get("behavioral_score"))
            st.json(data)
        except Exception as exc:
            st.error(f"Unable to fetch scores: {exc}")
