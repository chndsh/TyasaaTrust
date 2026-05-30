from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..utils.schema import FEATURE_COLUMNS


def make_synthetic(n=500, seed=42):
    rng = np.random.RandomState(seed)
    ids = [f"acct_{i:05d}" for i in range(n)]

    # base features
    data = {"account_id_hash": ids}
    for col in FEATURE_COLUMNS:
        if col == "account_id_hash":
            continue
        # create positive-skewed and bounded features
        data[col] = rng.normal(loc=0.5, scale=0.2, size=n).clip(0, 5)

    df = pd.DataFrame(data)

    # create a synthetic label correlated with some features
    score_signal = (
        1.5 * df.get("utility_payment_consistency", 0)
        - 0.8 * df.get("recharge_variance", 0)
        + 0.6 * df.get("seasonal_recovery_score", 0)
    )
    prob = 1 / (1 + np.exp(- (score_signal - score_signal.mean())))
    labels = (rng.rand(n) < prob).astype(int)

    df_train = df.copy()
    df_train["score"] = labels
    return df, df_train


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic features + training CSV")
    parser.add_argument("--out-dir", default="data/staged/csv", help="Output dir")
    parser.add_argument("--n", type=int, default=500)
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    feats, train = make_synthetic(n=args.n)
    feats.to_csv(out / "features.csv", index=False)
    train.to_csv(out / "training.csv", index=False)
    print(f"Wrote features.csv and training.csv to {out}")


if __name__ == "__main__":
    main()
