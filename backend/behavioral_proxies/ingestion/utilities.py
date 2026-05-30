from __future__ import annotations

import pandas as pd

from ..privacy.hashing import hash_account_id
from ..utils.schema import UTILITIES_COLUMNS


def normalize_utilities_payments(df: pd.DataFrame, secret: str) -> pd.DataFrame:
    missing = UTILITIES_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing utilities columns: {sorted(missing)}")

    df = df.copy()
    df["account_id_hash"] = df["account_id"].astype(str).apply(
        lambda value: hash_account_id(value, secret)
    )
    df = df.drop(columns=["account_id"])

    for col in ["billing_period_start", "billing_period_end", "payment_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    return df
