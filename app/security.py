import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.settings import settings

API_KEY_HEADER_NAME = "X-API-Key"

api_key_header = APIKeyHeader(
    name=API_KEY_HEADER_NAME,
    scheme_name="Telemetry API Key",
    description="Olay oluşturma işlemlerinde gerekli API anahtarı.",
    auto_error=False,
)


def require_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> str:
    configured_api_key = settings.telemetry_api_key

    if not configured_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured on the server.",
        )

    is_valid = api_key is not None and secrets.compare_digest(
        api_key.encode("utf-8"),
        configured_api_key.encode("utf-8"),
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "APIKey"},
        )

    return api_key
