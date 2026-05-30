from __future__ import annotations

import pandas as pd

from .cashflow_seasonality import compute_cashflow_seasonality
from .payments_consistency import compute_payment_consistency
from .topup_patterns import compute_topup_patterns


def build_feature_set(
    utilities_df: pd.DataFrame,
    topups_df: pd.DataFrame,
    seasonality_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    payments = compute_payment_consistency(utilities_df)
    topups = compute_topup_patterns(topups_df)
    seasonality = compute_cashflow_seasonality(topups_df, seasonality_df)

    features = payments.join(topups, how="outer").join(seasonality, how="outer")
    features.index.name = "account_id_hash"
    return features.reset_index()
