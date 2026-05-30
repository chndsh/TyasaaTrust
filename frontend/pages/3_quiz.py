import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Psychometric Quiz")
merchant_id = st.text_input("Merchant ID", value="merchant-demo")

questions = []
try:
    response = httpx.get(f"{API_URL}/psych/questions", timeout=10)
    response.raise_for_status()
    questions = response.json().get("questions", [])
except Exception:
    questions = []

responses = []
for idx, question in enumerate(questions):
    answer = st.radio(
        question.get("question", f"Question {idx + 1}"),
        question.get("options", ["Yes", "No"]),
        key=f"q_{idx}",
    )
    responses.append(
        {
            "question": question.get("question"),
            "answer": answer,
            "trait": question.get("trait"),
        }
    )

if st.button("Submit quiz"):
    payload = {"merchant_id": merchant_id, "responses": responses}
    try:
        submit = httpx.post(f"{API_URL}/psych/submit", json=payload, timeout=10)
        submit.raise_for_status()
        st.json(submit.json())
    except Exception as exc:
        st.error(f"Unable to submit quiz: {exc}")
