from typing import Any

from fastapi import APIRouter, BackgroundTasks,Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm


from src.auth import jwt, service, utils
from src.auth.dependencies import (
    valid_refresh_token,
    valid_refresh_token_user,
    valid_user_create,
)
from src.auth.jwt import parse_jwt_user_data
from src.auth.schemas import AccessTokenResponse, AuthUser, JWTData, UserResponse

router = APIRouter()


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(
    auth_data: AuthUser = Depends(valid_user_create),
) -> dict[str, str]:
    """
    Register a new user.

    Parameters:
    - auth_data: Authentication data of the user.

    Returns:
    - A dictionary containing the email of the registered user.
    """
    user = await service.create_user(auth_data)
    return {
        "email": user["email"],
    }


@router.get("/users/me", response_model=UserResponse)
async def get_my_account(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
) -> dict[str, str]:
    """
    Get the account information of the authenticated user.

    Parameters:
    - jwt_data: JWT data of the authenticated user.

    Returns:
    - A dictionary containing the email of the authenticated user.
    """
    user = await service.get_user_by_id(jwt_data.user_id)

    return {
        "email": user["email"],
    }


@router.post("/users/tokens", response_model=AccessTokenResponse)
async def auth_user(auth_data: AuthUser, response: Response) -> AccessTokenResponse:
    """
    Authenticate a user and generate access and refresh tokens.

    Parameters:
    - auth_data: Authentication data of the user.
    - response: HTTP response object.

    Returns:
    - An AccessTokenResponse object containing the access and refresh tokens.
    """
    user = await service.authenticate_user(auth_data)
    refresh_token_value = await service.create_refresh_token(user_id=user["_id"])

    response.set_cookie(**utils.get_refresh_token_settings(refresh_token_value))

    return AccessTokenResponse(
        access_token=jwt.create_access_token(user=user),
        refresh_token=refresh_token_value,
    )
    
@router.post("/users/swagger-auth", response_model=AccessTokenResponse)
async def swagger_auth(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> AccessTokenResponse:
    """
    Authenticate a user for Swagger UI authorization.
    
    Parameters:
    - response: HTTP response object.
    - form_data: Authentication data of the user (form data format).
    
    Returns:
    - An AccessTokenResponse object containing the access and refresh tokens.
    """
    user = await service.authenticate_user(AuthUser(
        email=form_data.username,  # Use the username as the email
        username=form_data.username,
        password=form_data.password,
    ))
    refresh_token_value = await service.create_refresh_token(user_id=user["_id"])
    response.set_cookie(**utils.get_refresh_token_settings(refresh_token_value))
    return AccessTokenResponse(
        access_token=jwt.create_access_token(user=user),
        refresh_token=refresh_token_value,
    )


@router.put("/users/tokens", response_model=AccessTokenResponse)
async def refresh_tokens(
    worker: BackgroundTasks,
    response: Response,
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
    user: dict[str, Any] = Depends(valid_refresh_token_user),
) -> AccessTokenResponse:
    """
    Refresh access and refresh tokens.

    Parameters:
    - worker: BackgroundTasks object for executing tasks in the background.
    - response: HTTP response object.
    - refresh_token: Refresh token data.
    - user: User data.

    Returns:
    - An AccessTokenResponse object containing the new access and refresh tokens.
    """
    refresh_token_value = await service.create_refresh_token(user_id=refresh_token["user_id"])
    response.set_cookie(**utils.get_refresh_token_settings(refresh_token_value))

    worker.add_task(service.expire_refresh_token, refresh_token["uuid"])
    return AccessTokenResponse(
        access_token=jwt.create_access_token(user=user),
        refresh_token=refresh_token_value,
    )


@router.delete("/users/tokens")
async def logout_user(
    response: Response,
    refresh_token: dict[str, Any] = Depends(valid_refresh_token),
) -> None:
    """
    Logout a user by expiring the refresh token.

    Parameters:
    - response: HTTP response object.
    - refresh_token: Refresh token data.
    """
    await service.expire_refresh_token(refresh_token["uuid"])

    response.delete_cookie(**utils.get_refresh_token_settings(refresh_token["refresh_token"], expired=True))
