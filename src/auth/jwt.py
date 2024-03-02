from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from auth.config import auth_config
from auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from auth.schemas import JWTData

# OAuth2 password bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/tokens", auto_error=False)


def create_access_token(
  *,
  user: dict[str, Any],
  expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
  """
  Create an access token for a user.

  Args:
    user: User data.
    expires_delta: Expiration time for the token.

  Returns:
    Access token as a string.
  """
  jwt_data = {
    "sub": str(user["_id"]),
    "exp": datetime.utcnow() + expires_delta,
    "is_admin": user.get("is_admin", False),
  }

  return jwt.encode(jwt_data, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)


async def parse_jwt_user_data_optional(
  token: str = Depends(oauth2_scheme),
) -> JWTData | None:
  """
  Parse the JWT user data from the token (optional).

  Args:
    token: JWT token.

  Returns:
    JWTData object containing the user data, or None if the token is not provided.
  """
  if not token:
    return None

  try:
    payload = jwt.decode(
      token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALG]
    )
  except JWTError:
    raise InvalidToken()

  return JWTData(**payload)


async def parse_jwt_user_data(
  token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> JWTData:
  """
  Parse the JWT user data from the token.

  Args:
    token: JWTData object containing the user data (optional).

  Returns:
    JWTData object containing the user data.

  Raises:
    AuthRequired: If the token is not provided.
  """
  if not token:
    raise AuthRequired()

  return token


async def parse_jwt_admin_data(
  token: JWTData = Depends(parse_jwt_user_data),
) -> JWTData:
  """
  Parse the JWT admin data from the token.

  Args:
    token: JWTData object containing the user data.

  Returns:
    JWTData object containing the user data.

  Raises:
    AuthorizationFailed: If the user is not an admin.
  """
  if not token.is_admin:
    raise AuthorizationFailed()

  return token


async def validate_admin_access(
  token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> None:
  """
  Validate admin access based on the token.

  Args:
    token: JWTData object containing the user data (optional).

  Raises:
    AuthorizationFailed: If the user is not an admin or the token is not provided.
  """
  if token and token.is_admin:
    return

  raise AuthorizationFailed()
