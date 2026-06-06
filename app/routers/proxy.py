"""
Drop-in proxy for OpenAI — change your base URL to this endpoint,
zero other code changes required.

Before:
    client = openai.OpenAI(base_url="https://api.openai.com/v1")

After:
    client = openai.OpenAI(
        base_url="https://your-headroom-api.com/v1/proxy/openai",
        api_key="hr_your_headroom_key",
        default_headers={"X-OpenAI-Key": "sk-your-openai-key"}
    )
"""

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
from app.middleware.auth import require_api_key
from app.compression import compress_messages
from app.database import record_usage

router = APIRouter(prefix="/v1/proxy", tags=["Proxy"])

OPENAI_BASE = "https://api.openai.com/v1"


@router.post(
    "/openai/chat/completions",
    summary="Drop-in OpenAI proxy with auto-compression",
    description="""
A transparent proxy to OpenAI's `/v1/chat/completions` that automatically
compresses your messages before forwarding. Change only your base URL —
all OpenAI parameters, models, and response formats are preserved.

Pass your OpenAI API key in the `X-OpenAI-Key` header.
    """,
)
async def proxy_openai(
    request: Request,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    api_key_record: dict = Depends(require_api_key),
):
    if not x_openai_key:
        raise HTTPException(status_code=400, detail="Pass your OpenAI key in the X-OpenAI-Key header.")

    body = await request.json()
    messages = body.get("messages", [])

    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in request body.")

    # Compress messages before forwarding
    compression_result = await compress_messages(messages)
    compressed_messages = compression_result["compressed_messages"]

    # Record usage
    await record_usage(
        api_key_record["key"],
        compression_result["tokens_in"],
        compression_result["tokens_out"],
    )

    # Forward to OpenAI with compressed messages
    forwarded_body = {**body, "messages": compressed_messages}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OPENAI_BASE}/chat/completions",
            json=forwarded_body,
            headers={
                "Authorization": f"Bearer {x_openai_key}",
                "Content-Type": "application/json",
            },
        )

    # Add compression stats to response headers
    result = response.json()
    headers = {
        "X-Headroom-Tokens-Saved": str(compression_result["tokens_saved"]),
        "X-Headroom-Reduction-Pct": str(compression_result["reduction_pct"]),
    }

    return JSONResponse(content=result, status_code=response.status_code, headers=headers)
