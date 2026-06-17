from __future__ import annotations

import numpy as np
from sklearn.metrics import brier_score_loss, roc_auc_score


def auc_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    return float(roc_auc_score(y_true, scores))


def brier_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    return float(brier_score_loss(y_true, scores))


def precision_at_k(y_true: np.ndarray, scores: np.ndarray, k: float = 0.1) -> float:
    if k <= 0:
        raise ValueError("k must be positive")

    n = len(scores)
    top_n = int(n * k) if k <= 1 else int(k)
    top_n = max(1, min(top_n, n))
    idx = np.argsort(scores)[-top_n:]
    return float(np.mean(y_true[idx]))
