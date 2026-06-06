from fastapi import Header, HTTPException, status
from app.database import get_api_key


async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> dict:
    """
    FastAPI dependency — validates the API key from the X-API-Key header.
    Raises 401 if missing or invalid, 403 if inactive.
    """
    if not x_api_key or not x_api_key.startswith("hr_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Keys should start with 'hr_'.",
        )

    record = await get_api_key(x_api_key)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found or inactive.",
        )

    return record
