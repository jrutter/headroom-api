from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Any
from app.middleware.auth import require_api_key
from app.compression import compress_messages
from app.database import record_usage

router = APIRouter(prefix="/v1", tags=["Compression"])


class CompressRequest(BaseModel):
    messages: list[dict[str, Any]] = Field(
        ...,
        description="Array of messages in OpenAI chat format: [{role, content}, ...]",
        example=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarise this document: [very long text...]"},
            {"role": "assistant", "content": "Here is the summary: [long response...]"},
        ],
    )


class CompressResponse(BaseModel):
    compressed_messages: list[dict[str, Any]]
    tokens_in: int
    tokens_out: int
    tokens_saved: int
    reduction_pct: float
    object: str = "compression"


@router.post(
    "/compress",
    response_model=CompressResponse,
    summary="Compress LLM context",
    description="""
Compress an array of LLM messages to reduce token count by 60–95% before sending to OpenAI or Anthropic.

**Usage:**
1. Collect your messages array as normal
2. POST to `/v1/compress`
3. Use `compressed_messages` in your LLM API call instead

**Auth:** Pass your API key in the `X-API-Key` header.
    """,
)
async def compress(
    body: CompressRequest,
    api_key_record: dict = Depends(require_api_key),
):
    result = await compress_messages(body.messages)

    # Record usage for billing
    await record_usage(
        api_key_record["key"],
        result["tokens_in"],
        result["tokens_out"],
    )

    return CompressResponse(**result)
