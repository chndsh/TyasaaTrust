from __future__ import annotations

import hashlib
import hmac
from typing import Iterable


def hash_account_id(account_id: str, secret: str) -> str:
    if not secret:
        raise ValueError("Secret is required for hashing account_id")

    return hmac.new(
        secret.encode("utf-8"),
        account_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def hash_with_keyring(account_id: str, secrets: Iterable[str]) -> list[str]:
    return [hash_account_id(account_id, secret) for secret in secrets]
