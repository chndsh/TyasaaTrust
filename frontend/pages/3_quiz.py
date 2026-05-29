import streamlit as st
import httpx

API = "http://backend:8000"

st.header("📋 Merchant Trust Assessment")
st.caption("Takes about 3 minutes. Answer honestly — there are no wrong answers.")

merchant_id = st.text_input("Your merchant ID", value="00000000-0000-0000-0000-000000000001")

# Load questions from backend
@st.cache_data
def load_questions():
    r = httpx.get(f"{API}/psych/questions")
    return r.json()["questions"]

questions = load_questions()
answers = {}

with st.form("quiz_form"):
    for q in questions:
        st.markdown(f"**{q['text_en']}**")
        st.caption(q["text_np"])                    # Nepali translation below
        answers[q["id"]] = st.radio(
            label="",
            options=q["options"],
            key=f"q_{q['id']}",
            label_visibility="collapsed"
        )
        st.divider()

    submitted = st.form_submit_button("Submit Assessment", use_container_width=True)

if submitted:
    responses = [
        {
            "question": q["text_en"],
            "answer": answers[q["id"]],
            "trait": q["trait"]
        }
        for q in questions
    ]

    with st.spinner("Analyzing your responses..."):
        r = httpx.post(f"{API}/psych/submit", json={
            "merchant_id": merchant_id,
            "responses": responses
        })

    if r.status_code == 200:
        data = r.json()
        st.success("Assessment complete!")
        st.metric("Psychometric Score", f"{data['psych_score']} / 100")
        st.info(data["summary"])

        with st.expander("Trait breakdown"):
            for trait, score in data["traits"].items():
                st.progress(score, text=f"{trait.replace('_', ' ').title()}: {score:.0%}")
    else:
        st.error("Something went wrong. Please try again.")