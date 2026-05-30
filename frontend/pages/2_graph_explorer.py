import os
import sys

# Compute the absolute path to the project root directory (TyasaaTrust/)
# Assumes the file is located inside frontend/ or frontend/pages/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".." if "pages" not in current_dir else "../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
