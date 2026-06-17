from __future__ import annotations

import os


def get_google_ai_api_key() -> str:
    key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_AI_STUDIO_API_KEY is not set")
    return key
