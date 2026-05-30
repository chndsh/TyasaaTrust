import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.behavioral_proxies.features.topup_patterns import (  # noqa: E402
    compute_topup_patterns,
)


def test_compute_topup_patterns_columns():
    df = pd.DataFrame(
        {
            "account_id_hash": ["a", "a", "b"],
            "topup_ts": ["2024-01-01", "2024-01-15", "2024-02-01"],
            "topup_amount": [10, 20, 15],
        }
    )
    result = compute_topup_patterns(df)
    expected = {
        "topup_freq_per_month",
        "median_topup_amount",
        "large_topup_ratio",
        "burstiness",
        "recharge_variance",
    }
    assert expected.issubset(result.columns)
