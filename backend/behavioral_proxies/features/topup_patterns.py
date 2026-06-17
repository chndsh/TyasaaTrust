"""Shim: re-export `compute_topup_patterns` from package-level features.

This keeps existing import paths stable while the implementation lives in
`backend.behavioral_proxies.features`.
"""

from . import compute_topup_patterns  # type: ignore

__all__ = ["compute_topup_patterns"]
