import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Trust Score Dashboard")
merchant_id = st.text_input(
    "Merchant ID",
    value="9800000000",
    max_chars=10,
    help="Enter the 10-digit merchant ID.",
)

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
