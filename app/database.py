"""
Database layer — mocked for local dev, swap in real Supabase credentials to go live.

Schema (run in Supabase SQL editor):

    create table api_keys (
        id uuid primary key default gen_random_uuid(),
        key text unique not null,
        user_id text not null,
        name text,
        tokens_in bigint default 0,
        tokens_out bigint default 0,
        stripe_customer_id text,
        plan text default 'starter',
        created_at timestamptz default now(),
        is_active boolean default true
    );
"""

import secrets
import hashlib
from typing import Optional
from datetime import datetime

# In-memory mock store (resets on restart — replace with Supabase)
_mock_keys: dict[str, dict] = {}


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    return f"hr_{secrets.token_urlsafe(32)}"


async def create_api_key(user_id: str, name: str = "default", plan: str = "starter") -> dict:
    """Create a new API key and store it."""
    key = generate_api_key()
    record = {
        "id": secrets.token_hex(8),
        "key": key,
        "key_hash": _hash_key(key),
        "user_id": user_id,
        "name": name,
        "tokens_in": 0,
        "tokens_out": 0,
        "plan": plan,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    _mock_keys[_hash_key(key)] = record

    # TODO: replace with Supabase:
    # supabase.table("api_keys").insert(record).execute()

    return record


async def get_api_key(key: str) -> Optional[dict]:
    """Look up an API key. Returns None if not found or inactive."""
    record = _mock_keys.get(_hash_key(key))

    # TODO: replace with Supabase:
    # result = supabase.table("api_keys").select("*").eq("key_hash", _hash_key(key)).single().execute()
    # record = result.data

    if record and record.get("is_active"):
        return record
    return None


async def record_usage(key: str, tokens_in: int, tokens_out: int):
    """Increment usage counters for an API key."""
    key_hash = _hash_key(key)
    if key_hash in _mock_keys:
        _mock_keys[key_hash]["tokens_in"] += tokens_in
        _mock_keys[key_hash]["tokens_out"] += tokens_out

    # TODO: replace with Supabase:
    # supabase.rpc("increment_usage", {"key_hash": key_hash, "t_in": tokens_in, "t_out": tokens_out}).execute()


async def get_usage(key: str) -> dict:
    """Get current usage stats for an API key."""
    record = _mock_keys.get(_hash_key(key))
    if not record:
        return {"tokens_in": 0, "tokens_out": 0}
    return {"tokens_in": record["tokens_in"], "tokens_out": record["tokens_out"]}
