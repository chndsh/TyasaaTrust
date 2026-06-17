"""Shim: re-export `compute_payment_consistency` from package-level features."""

from . import compute_payment_consistency  # type: ignore

__all__ = ["compute_payment_consistency"]
