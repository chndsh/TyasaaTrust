import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


SCORING_PROMPT = """
You are a financial psychologist evaluating a micro-merchant's creditworthiness
based on their answers to situational questions.

Here are their responses:
{responses}

Score the merchant on each of these four traits from 0.0 to 1.0:
- conscientiousness: how organized, disciplined, and reliable they are
- risk_aversion: how carefully they manage financial risk
- future_orientation: how much they prioritize long-term stability over short-term gain
- social_trust: how they balance relationships with financial boundaries

Return ONLY a JSON object with no explanation, like this:
{{
  "conscientiousness": 0.75,
  "risk_aversion": 0.60,
  "future_orientation": 0.80,
  "social_trust": 0.65,
  "summary": "One sentence in plain English describing this merchant's financial character."
}}
"""


def score_responses(responses: list[dict]) -> dict:
    """
    responses: [{"question": "...", "answer": "...", "trait": "..."}, ...]
    Returns trait scores and a plain-language summary.
    """
    formatted = "\n".join(
        f"Q: {r['question']}\nA: {r['answer']} (testing: {r['trait']})"
        for r in responses
    )
    prompt = SCORING_PROMPT.format(responses=formatted)

    result = model.generate_content(prompt)
    raw = result.text.strip()

    # Strip markdown code fences if Gemini adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    traits = json.loads(raw.strip())

    # Compute a single 0–100 psychometric score
    weights = {
        "conscientiousness": 0.35,
        "risk_aversion": 0.25,
        "future_orientation": 0.25,
        "social_trust": 0.15,
    }
    psych_score = sum(traits[k] * w for k, w in weights.items()) * 100

    return {
        "traits": {k: traits[k] for k in weights},
        "psych_score": round(psych_score, 2),
        "summary": traits.get("summary", "")
    }