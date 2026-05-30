import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Tyasaa Trust", layout="wide")

st.title("Tyasaa Trust Layer")
st.write("Use the sidebar to explore each module independently.")
st.info(f"Backend API: {API_URL}")
