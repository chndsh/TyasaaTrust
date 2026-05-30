import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Social Graph Explorer")
merchant_id = st.text_input("Merchant ID", value="merchant-demo")

if st.button("Fetch social score"):
    with st.spinner("Loading social graph score..."):
        try:
            response = httpx.get(f"{API_URL}/graph/{merchant_id}", timeout=10)
            response.raise_for_status()
            st.json(response.json())
        except Exception as exc:
            st.error(f"Unable to reach backend: {exc}")
