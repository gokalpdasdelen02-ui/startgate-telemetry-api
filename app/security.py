import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from app.settings import settings

from loguru import logger

API_KEY_HEADER_NAME = "X-API-Key"

api_key_header = APIKeyHeader(
    name=API_KEY_HEADER_NAME,
    scheme_name="Telemetry API Key",
    description="Telemetri olaylarını oluşturma ve sorgulama "
    "İşlemlerinde gerekili API anahtarı",
    auto_error=False,
)


def require_api_key(
    request: Request,
    api_key: Annotated[str | None, Depends(api_key_header)],
) -> str:
    configured_api_key = settings.telemetry_api_key

    if not configured_api_key:

        logger.bind(
            method=request.method,
            path=request.url.path,
            setting_name="telemetry_api_key",
        ).error("api_key_configuration_missing")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key is not configured on the server.",
        )

    is_valid = api_key is not None and secrets.compare_digest(
        api_key.encode("utf-8"),
        configured_api_key.encode("utf-8"),
    )

    if not is_valid:
        logger.bind(
            method=request.method,
            path=request.url.path,
            api_key_provided=api_key is not None,
        ).warning("api_key_authentication_failed")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "APIKey"},
        )

    return api_key
