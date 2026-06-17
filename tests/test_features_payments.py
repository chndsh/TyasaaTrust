import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.behavioral_proxies.features.payments_consistency import (  # noqa: E402
    compute_payment_consistency,
)


def test_compute_payment_consistency_columns():
    df = pd.DataFrame(
        {
            "account_id_hash": ["a", "a", "b"],
            "payment_date": ["2024-01-10", "2024-02-10", "2024-01-05"],
            "billing_period_end": ["2023-12-31", "2024-01-31", "2023-12-31"],
            "billed_amount": [50, 50, 25],
            "payment_amount": [50, 40, 25],
        }
    )
    result = compute_payment_consistency(df)
    expected = {
        "on_time_ratio",
        "utility_payment_consistency",
        "std_interpayment_days",
        "missed_count",
        "payment_amount_cv",
        "days_since_last_payment",
    }
    assert expected.issubset(result.columns)
