"""Refresh token storage using Redis with automatic TTL expiry."""

import hashlib
import json

from app.config import settings
from app.db.redis import get_redis


def hash_token(token: str) -> str:
    """SHA-256 hash a raw refresh token."""
    return hashlib.sha256(token.encode()).hexdigest()


def _token_key(token_hash: str) -> str:
    """Redis key for a specific refresh token."""
    return f"refresh:{token_hash}"


def _user_tokens_key(user_id: str) -> str:
    """Redis key for a user's set of active refresh token hashes."""
    return f"user_tokens:{user_id}"


async def store_refresh_token(
    user_id: str,
    raw_token: str,
) -> None:
    """Store a hashed refresh token in Redis with TTL.

    Two keys are created:
    1. `refresh:<hash>` -> JSON with user_id (expires with TTL)
    2. `user_tokens:<user_id>` -> Set of active token hashes (for revoke-all)
    """
    r = get_redis()
    token_h = hash_token(raw_token)
    ttl_seconds = settings.REFRESH_TOKEN_EXPIRY_DAYS * 86400

    # Store token data with TTL (auto-deletes on expiry)
    await r.set(
        _token_key(token_h),
        json.dumps({"user_id": user_id}),
        ex=ttl_seconds,
    )

    # Add to user's token set (for revoke-all-sessions)
    await r.sadd(_user_tokens_key(user_id), token_h)
    # Set TTL on the user set too (cleanup, refreshed on each login)
    await r.expire(_user_tokens_key(user_id), ttl_seconds)


async def get_valid_refresh_token(raw_token: str) -> dict | None:
    """Look up a refresh token by its hash. Returns {"user_id": ...} or None.

    Returns None if the token doesn't exist (expired or revoked).
    No need to check expiry -- Redis TTL handles that automatically.
    """
    r = get_redis()
    token_h = hash_token(raw_token)
    data = await r.get(_token_key(token_h))
    if data is None:
        return None
    return json.loads(data)


async def revoke_refresh_token(raw_token: str, user_id: str | None = None) -> None:
    """Revoke a specific refresh token by deleting it from Redis."""
    r = get_redis()
    token_h = hash_token(raw_token)

    # Delete the token key
    await r.delete(_token_key(token_h))

    # Remove from user's token set (if user_id known)
    if user_id:
        await r.srem(_user_tokens_key(user_id), token_h)


async def revoke_all_user_tokens(user_id: str) -> None:
    """Revoke all refresh tokens for a user (e.g., on password change).

    Looks up all token hashes in the user's set and deletes them.
    """
    r = get_redis()
    user_key = _user_tokens_key(user_id)

    # Get all token hashes for this user
    token_hashes = await r.smembers(user_key)

    if token_hashes:
        # Delete all individual token keys
        keys_to_delete = [_token_key(h) for h in token_hashes]
        await r.delete(*keys_to_delete)

    # Delete the user's token set itself
    await r.delete(user_key)
