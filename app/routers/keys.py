from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.middleware.auth import require_api_key
from app.database import create_api_key, get_usage

router = APIRouter(prefix="/v1/keys", tags=["API Keys"])


class CreateKeyRequest(BaseModel):
    user_id: str
    name: str = "default"
    plan: str = "starter"


class UsageResponse(BaseModel):
    tokens_in: int
    tokens_out: int
    tokens_saved: int
    reduction_pct: float


@router.post("/", summary="Create a new API key")
async def create_key(body: CreateKeyRequest):
    """Create a new API key. In production this would be gated behind auth."""
    record = await create_api_key(body.user_id, body.name, body.plan)
    return {
        "key": record["key"],
        "name": record["name"],
        "plan": record["plan"],
        "created_at": record["created_at"],
        "message": "Store this key securely — it won't be shown again.",
    }


@router.get("/usage", summary="Get usage stats for current key")
async def get_key_usage(api_key_record: dict = Depends(require_api_key)):
    """Returns token usage stats for the authenticated API key."""
    usage = await get_usage(api_key_record["key"])
    tokens_saved = usage["tokens_in"] - usage["tokens_out"]
    reduction_pct = (
        round((tokens_saved / usage["tokens_in"]) * 100, 1)
        if usage["tokens_in"] > 0
        else 0.0
    )
    return UsageResponse(
        tokens_in=usage["tokens_in"],
        tokens_out=usage["tokens_out"],
        tokens_saved=tokens_saved,
        reduction_pct=reduction_pct,
    )
