import random
import string

from typing import Any

from auth.config import auth_config
from config import settings

ALPHA_NUM = string.ascii_letters + string.digits

def generate_random_alphanum(length: int = 20) -> str:
  """
  Generates a random alphanumeric string of specified length.

  Args:
    length (int): Length of the generated string. Default is 20.

  Returns:
    str: Random alphanumeric string.
  """
  return "".join(random.choices(ALPHA_NUM, k=length))


def get_refresh_token_settings(
  refresh_token: str,
  expired: bool = False,
) -> dict[str, Any]:
  """
  Returns the settings for the refresh token cookie.

  Args:
    refresh_token (str): Refresh token value.
    expired (bool): Flag indicating if the token is expired. Default is False.

  Returns:
    dict[str, Any]: Refresh token cookie settings.
  """
  base_cookie = {
    "key": auth_config.REFRESH_TOKEN_KEY,
    "httponly": True,
    "samesite": "none",
    #"samesite": "lax",
    "secure": auth_config.SECURE_COOKIES,
    "domain": settings.SITE_DOMAIN,
  }
  if expired:
    return base_cookie

  return {
    **base_cookie,
    "value": refresh_token,
    "max_age": auth_config.REFRESH_TOKEN_EXP,
  }
