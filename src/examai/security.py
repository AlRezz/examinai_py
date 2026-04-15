"""Password hashing and verification (bcrypt, docs/data-models.md)."""

from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    data = plain.encode("utf-8")
    hashed = bcrypt.hashpw(data, bcrypt.gensalt(rounds=12))
    return hashed.decode("ascii")


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            password_hash.encode("ascii"),
        )
    except ValueError:
        return False
