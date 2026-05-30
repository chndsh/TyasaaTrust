from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

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


def run(out_dir: Path | str = "data/staged/csv") -> dict:
    out_dir = Path(out_dir)
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

    explanations = generate_shap_explanations(
        model, feats
    )
    explanations_to_json(
        explanations, Path("data/staged/explanations.json")
    )

    scored = score_accounts(model, feats)
    scored_path = Path("data/staged/scored.csv")
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
