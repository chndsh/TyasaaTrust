from __future__ import annotations

from typing import Iterable

import pandas as pd


def enforce_min_group_size(
    df: pd.DataFrame, group_cols: Iterable[str], min_size: int = 5
) -> pd.DataFrame:
    group_cols = list(group_cols)
    if not group_cols:
        raise ValueError("group_cols cannot be empty")

    counts = df.groupby(group_cols).size().rename("group_size")
    eligible = counts[counts >= min_size].index
    return df.set_index(group_cols).loc[eligible].reset_index()
