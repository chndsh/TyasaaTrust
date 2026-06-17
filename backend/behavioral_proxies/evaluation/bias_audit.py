from __future__ import annotations

import pandas as pd


def group_error_rates(
    df: pd.DataFrame,
    label_col: str,
    score_col: str,
    group_col: str,
    threshold: float = 0.5,
) -> pd.DataFrame:
    data = df.copy()
    data["pred"] = data[score_col] >= threshold
    data["label"] = data[label_col].astype(bool)

    def _rates(group: pd.DataFrame) -> pd.Series:
        fp = ((group["pred"] == 1) & (group["label"] == 0)).sum()
        fn = ((group["pred"] == 0) & (group["label"] == 1)).sum()
        tn = ((group["pred"] == 0) & (group["label"] == 0)).sum()
        tp = ((group["pred"] == 1) & (group["label"] == 1)).sum()
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        fnr = fn / (fn + tp) if (fn + tp) else 0.0
        return pd.Series({"fp": fp, "fn": fn, "fpr": fpr, "fnr": fnr})

    return data.groupby(group_col).apply(_rates).reset_index()
