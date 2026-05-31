from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Support direct execution from the repository root or this file path.
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_root not in sys.path:
    sys.path.insert(0, package_root)

from models.train import (
    train_xgboost_with_validation,
    save_model,
    train_logistic_regression,
)
from evaluation.explain import (
    generate_shap_explanations,
    explanations_to_json,
)
from models.predict import score_accounts
from utils.schema import FEATURE_COLUMNS


def _ensure_input_data(out_dir: Path) -> None:
    feats_path = out_dir / "features.csv"
    train_path = out_dir / "training.csv"

    if feats_path.exists() and train_path.exists():
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n_rows = 250
    account_ids = [f"acct_{idx:05d}" for idx in range(n_rows)]

    features = pd.DataFrame({"account_id_hash": account_ids})
    for column in FEATURE_COLUMNS:
        if column == "account_id_hash":
            continue
        features[column] = rng.normal(loc=0.5, scale=0.2, size=n_rows).clip(0, 5)

    score_signal = (
        1.5 * features.get("utility_payment_consistency", 0)
        - 0.8 * features.get("recharge_variance", 0)
        + 0.6 * features.get("seasonal_recovery_score", 0)
    )
    probabilities = 1 / (1 + np.exp(-(score_signal - score_signal.mean())))
    labels = (rng.random(n_rows) < probabilities).astype(int)

    features.to_csv(feats_path, index=False)
    pd.DataFrame({"score": labels}).to_csv(train_path, index=False)


def run(out_dir: Path | str = "data/staged/csv") -> dict:
    out_dir = Path(out_dir)
    _ensure_input_data(out_dir)
    feats_path = out_dir / "features.csv"
    train_path = out_dir / "training.csv"

    if not feats_path.exists() or not train_path.exists():
        raise RuntimeError(
            "features.csv and training.csv must exist in out_dir"
        )

    feats = pd.read_csv(feats_path)
    train = pd.read_csv(train_path)

    X = feats.copy()
    y = train["score"]

    try:
        model, metrics = train_xgboost_with_validation(X, y)
    except TypeError:
        # fallback for xgboost versions without early-stopping support
        model = train_logistic_regression(X, y)
        metrics = {"fallback": "logistic_regression"}
    model_path = Path("models") / "xgb_smoke.pkl"
    save_model(model, model_path)

    output_dir = Path("data/staged")
    output_dir.mkdir(parents=True, exist_ok=True)

    explanations = generate_shap_explanations(
        model, feats
    )
    explanations_to_json(
        explanations, output_dir / "explanations.json"
    )

    scored = score_accounts(model, feats)
    scored_path = output_dir / "scored.csv"
    scored.to_csv(scored_path, index=False)

    result = {
        "model_path": str(model_path),
        "metrics": metrics,
        "scored_csv": str(scored_path),
    }
    return result


if __name__ == "__main__":
    import json
    res = run()
    print(json.dumps(res, indent=2))
