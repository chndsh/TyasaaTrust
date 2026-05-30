from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap


def _unwrap_shap_values(shap_values: Any) -> np.ndarray:
    # shap_values may be a list (per-class) or an array
    if isinstance(shap_values, list) or isinstance(shap_values, tuple):
        # take the last class (usually positive class for binary)
        return np.asarray(shap_values[-1])
    return np.asarray(shap_values)


def generate_shap_explanations(
    model: Any, features_df: pd.DataFrame, top_k: int = 5
) -> pd.DataFrame:
    """Generate SHAP explanations for each row in `features_df`.

    Returns a DataFrame with columns: `account_id_hash`, `score`, `top_pos`, `top_neg`, `raw_shap`.
    """
    if features_df.empty:
        return pd.DataFrame(
            columns=["account_id_hash", "score", "top_pos", "top_neg", "raw_shap"]
        )

    data = features_df.copy()
    account_ids = None
    if "account_id_hash" in data.columns:
        account_ids = data.pop("account_id_hash").astype(str)

    X = data.fillna(0)

    # Create explainer (TreeExplainer for tree models, generic for others)
    try:
        explainer = shap.TreeExplainer(model)
    except Exception:
        # shap.Explainer expects either a model object it understands or a
        # callable. Wrap sklearn Pipelines / non-tree estimators into a
        # callable that returns a 1-D score/probability so SHAP can run.
        if hasattr(model, "predict_proba"):
            def _model_callable(data):
                return model.predict_proba(data)[:, 1]

            explainer = shap.Explainer(_model_callable, X)
        elif hasattr(model, "predict"):
            def _model_callable(data):
                return model.predict(data)

            explainer = shap.Explainer(_model_callable, X)
        else:
            explainer = shap.Explainer(model, X)

    # Compute shap values
    try:
        raw_shap = explainer.shap_values(X)
    except Exception:
        # shap.Explainer returns an object when called
        out = explainer(X)
        raw_shap = out.values

    shap_vals = _unwrap_shap_values(raw_shap)

    # Scores
    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(X)[:, 1]
    else:
        scores = model.predict(X)

    cols = X.columns.tolist()
    rows = []
    for i in range(len(X)):
        sv = shap_vals[i]
        feature_imp = list(zip(cols, sv.tolist()))
        feature_imp_sorted = sorted(
            feature_imp, key=lambda x: abs(x[1]), reverse=True
        )

        top_pos = [
            {"feature": f, "impact": float(v)}
            for f, v in feature_imp_sorted[:top_k]
            if v > 0
        ]
        top_neg = [
            {"feature": f, "impact": float(v)}
            for f, v in feature_imp_sorted[:top_k]
            if v < 0
        ]

        rows.append(
            {
                "account_id_hash": (
                    account_ids.iloc[i] if account_ids is not None else None
                ),
                "score": (
                    float(scores[i])
                    if hasattr(scores[i], "__float__")
                    else float(scores[i])
                ),
                "top_pos": top_pos,
                "top_neg": top_neg,
                "raw_shap": {cols[j]: float(sv[j]) for j in range(len(cols))},
            }
        )

    return pd.DataFrame(rows)


def explanations_to_json(df: pd.DataFrame, out_path: str | Path) -> None:
    out = df.to_dict(orient="records")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)