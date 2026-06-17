from __future__ import annotations

import pandas as pd

from ..utils.schema import SEASONALITY_COLUMNS


def normalize_seasonality_calendar(df: pd.DataFrame) -> pd.DataFrame:
    missing = SEASONALITY_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing seasonality columns: {sorted(missing)}")

    df = df.copy()
    df["season_start_month"] = df["season_start_month"].astype(int)
    df["season_end_month"] = df["season_end_month"].astype(int)

    return df
