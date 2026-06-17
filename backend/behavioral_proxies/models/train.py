from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - optional dependency fallback
    XGBClassifier = None


def _feature_frame(X: pd.DataFrame) -> pd.DataFrame:
    numeric = X.select_dtypes(include=[np.number]).copy()
    if numeric.empty:
        raise ValueError("Training features must contain at least one numeric column")
    return numeric.fillna(0)


def _build_validation_split(
    X: pd.DataFrame, y: pd.Series | pd.DataFrame | np.ndarray
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    y_series = pd.Series(y).reset_index(drop=True)
    X_frame = _feature_frame(X).reset_index(drop=True)

    stratify = y_series if y_series.nunique() > 1 else None
    return train_test_split(
        X_frame,
        y_series,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )


def _compute_metrics(y_true: pd.Series, y_prob: np.ndarray) -> dict[str, float]:
    metrics: dict[str, float] = {}
    try:
        metrics["auc"] = float(roc_auc_score(y_true, y_prob))
    except Exception:
        metrics["auc"] = float("nan")

    try:
        metrics["brier"] = float(brier_score_loss(y_true, y_prob))
    except Exception:
        metrics["brier"] = float("nan")

    threshold = np.quantile(y_prob, 0.9) if len(y_prob) else 0.5
    try:
        metrics["precision_at_10p"] = float(
            precision_score(y_true, (y_prob >= threshold).astype(int), zero_division=0)
        )
    except Exception:
        metrics["precision_at_10p"] = float("nan")

    return metrics


def train_xgboost_with_validation(X: pd.DataFrame, y: pd.Series | np.ndarray) -> tuple[Any, dict[str, float]]:
    X_train, X_valid, y_train, y_valid = _build_validation_split(X, y)

    if XGBClassifier is None:
        model = train_logistic_regression(X_train, y_train)
        valid_prob = model.predict_proba(X_valid)[:, 1]
        return model, _compute_metrics(y_valid, valid_prob)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
    )
    model.fit(X_train, y_train)
    valid_prob = model.predict_proba(X_valid)[:, 1]
    return model, _compute_metrics(y_valid, valid_prob)


def train_logistic_regression(X: pd.DataFrame, y: pd.Series | np.ndarray) -> Pipeline:
    X_frame = _feature_frame(X)
    y_series = pd.Series(y).reset_index(drop=True)

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=1000, class_weight="balanced"),
            ),
        ]
    )
    model.fit(X_frame, y_series)
    return model


def save_model(model: Any, model_path: str | Path) -> None:
    path = Path(model_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(model, handle)
