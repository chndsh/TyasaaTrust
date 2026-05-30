from __future__ import annotations

import pandas as pd

from ..privacy.hashing import hash_account_id
from ..utils.schema import AIRTIME_COLUMNS


def normalize_airtime_topups(df: pd.DataFrame, secret: str) -> pd.DataFrame:
    missing = AIRTIME_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing airtime columns: {sorted(missing)}")

    df = df.copy()
    df["account_id_hash"] = df["account_id"].astype(str).apply(
        lambda value: hash_account_id(value, secret)
    )
    df = df.drop(columns=["account_id"])
    df["topup_ts"] = pd.to_datetime(df["topup_ts"], errors="coerce")
    df = df[df["topup_amount"] >= 0]

    return df
