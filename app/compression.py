"""
Headroom compression wrapper.
Real docs: https://github.com/chopratejas/headroom
"""

from typing import Any

# Try to import Headroom — fall back to mock if not installed
try:
    from headroom import compress as _headroom_compress
    HEADROOM_AVAILABLE = True
except ImportError:
    HEADROOM_AVAILABLE = False


def _count_tokens(messages: list[dict]) -> int:
    """Rough token estimate (4 chars ≈ 1 token)."""
    total = sum(len(str(m.get("content", ""))) for m in messages)
    return max(1, total // 4)


def _mock_compress(messages: list[dict]) -> list[dict]:
    """
    Mock compressor for local dev — simulates ~60% compression
    by trimming long assistant messages.
    Replace with real Headroom once installed.
    """
    compressed = []
    for msg in messages:
        content = str(msg.get("content", ""))
        if msg.get("role") == "assistant" and len(content) > 200:
            # Simulate compression: keep first ~40% of long assistant messages
            trimmed = content[: int(len(content) * 0.4)] + " [compressed]"
            compressed.append({**msg, "content": trimmed})
        else:
            compressed.append(msg)
    return compressed


async def compress_messages(messages: list[dict[str, Any]]) -> dict:
    """
    Compress a list of LLM messages using Headroom.
    Returns compressed messages + stats.
    """
    tokens_in = _count_tokens(messages)

    if HEADROOM_AVAILABLE:
        # Real Headroom compression
        compressed = _headroom_compress(messages)
    else:
        # Mock compression for local dev
        compressed = _mock_compress(messages)

    tokens_out = _count_tokens(compressed)
    tokens_saved = max(0, tokens_in - tokens_out)
    reduction_pct = round((tokens_saved / tokens_in) * 100, 1) if tokens_in > 0 else 0.0

    return {
        "compressed_messages": compressed,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "tokens_saved": tokens_saved,
        "reduction_pct": reduction_pct,
        "headroom_available": HEADROOM_AVAILABLE,
    }
