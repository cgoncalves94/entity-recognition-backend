from datetime import datetime
from typing import Any

from fastapi import Cookie, Depends

from src.auth import service
from src.auth.exceptions import EmailTaken, RefreshTokenNotValid
from src.auth.schemas import AuthUser


# Validates if the user is valid to be created
async def valid_user_create(user: AuthUser) -> AuthUser:
    """
    Validates if the user is valid to be created.
    Raises an EmailTaken exception if the user's email already exists.
    """
    if await service.get_user_by_email(user.email):
        raise EmailTaken()

    return user


# Checks if the refresh token is still valid based on the expiration time
def _is_valid_refresh_token(db_refresh_token: dict[str, Any]) -> bool:
    """
    Checks if the refresh token is still valid based on the expiration time.
    Returns True if the refresh token is still valid, False otherwise.
    """
    return datetime.utcnow() <= db_refresh_token["expires_at"]


# Validates if the refresh token is valid
async def valid_refresh_token(
    refresh_token: str = Cookie(..., alias="refreshToken"),
) -> dict[str, Any]:
    """
    Validates if the refresh token is valid.
    Raises a RefreshTokenNotValid exception if the refresh token is not found or expired.
    """
    db_refresh_token = await service.get_refresh_token(refresh_token)
    if not db_refresh_token:
        raise RefreshTokenNotValid()

    if not _is_valid_refresh_token(db_refresh_token):
        raise RefreshTokenNotValid()

    return db_refresh_token


# Validates if the refresh token user is valid
async def valid_refresh_token_user(
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
) -> dict[str, Any]:
    """
    Validates if the refresh token user is valid.
    Raises a RefreshTokenNotValid exception if the user associated with the refresh token is not found.
    """
    user = await service.get_user_by_id(refresh_token["user_id"])
    if not user:
        raise RefreshTokenNotValid()

    return user
