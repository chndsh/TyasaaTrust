import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.behavioral_proxies.features import (  # noqa: E402
    compute_cashflow_seasonality,
)


def test_compute_cashflow_seasonality_columns():
    topups = pd.DataFrame(
        {
            "account_id_hash": ["a", "a", "b"],
            "topup_ts": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "topup_amount": [100, 150, 120],
        }
    )
    result = compute_cashflow_seasonality(topups)
    expected = {
        "seasonal_amplitude",
        "harvest_aligned_spike",
        "rolling_monthly_variance",
        "seasonal_recovery_score",
    }
    assert expected.issubset(result.columns)


def test_compute_cashflow_seasonality_uses_calendar():
    topups = pd.DataFrame(
        {
            "account_id_hash": ["a", "a", "a"],
            "region_id": ["r1", "r1", "r1"],
            "topup_ts": ["2024-01-01", "2024-02-01", "2024-04-01"],
            "topup_amount": [100, 150, 50],
        }
    )
    calendar = pd.DataFrame(
        {
            "region_id": ["r1"],
            "season_label": ["harvest"],
            "season_start_month": [1],
            "season_end_month": [2],
        }
    )

    result = compute_cashflow_seasonality(topups, calendar)

    assert result.loc["a", "harvest_aligned_spike"] == 0.8333333333333334
