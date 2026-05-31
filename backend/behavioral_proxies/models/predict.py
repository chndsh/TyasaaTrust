from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _feature_frame(features_df: pd.DataFrame) -> pd.DataFrame:
    frame = features_df.copy()
    if "account_id_hash" in frame.columns:
        frame = frame.drop(columns=["account_id_hash"])
    return frame.select_dtypes(include=[np.number]).fillna(0)


def score_accounts(model: Any, features_df: pd.DataFrame) -> pd.DataFrame:
    frame = _feature_frame(features_df)
    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(frame)[:, 1]
    else:
        raw_scores = model.predict(frame)
        scores = np.asarray(raw_scores, dtype=float)

    scored = features_df.copy()
    scored["score"] = np.clip(scores, 0.0, 1.0)
    if "account_id_hash" not in scored.columns:
        scored.insert(0, "account_id_hash", [f"row_{idx:05d}" for idx in range(len(scored))])

    ordered_columns = ["account_id_hash", "score"]
    ordered_columns.extend(
        column for column in scored.columns if column not in {"account_id_hash", "score"}
    )
    return scored[ordered_columns]
