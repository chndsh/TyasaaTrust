from __future__ import annotations

import os
from typing import Iterable

import pandas as pd


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def require_columns(df: pd.DataFrame, required: Iterable[str], label: str) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{label} is missing columns: {sorted(missing)}")
