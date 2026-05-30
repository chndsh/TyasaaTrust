"""Shim: re-export `compute_cashflow_seasonality` from package-level features."""

from . import compute_cashflow_seasonality  # type: ignore

__all__ = ["compute_cashflow_seasonality"]
