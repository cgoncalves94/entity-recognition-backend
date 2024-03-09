from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

from src.constants import Environment


class Config(BaseSettings):
  """
  Configuration class for the application.
  """

  DATABASE_URL: str
  DATABASE_NAME: str

  SITE_DOMAIN: str = "myapp.com"

  ENVIRONMENT: Environment = Environment.PRODUCTION

  SENTRY_DSN: str | None = None

  CORS_ORIGINS: list[str]
  CORS_ORIGINS_REGEX: str | None = None
  CORS_HEADERS: list[str]

  APP_VERSION: str = "1"

  @field_validator("DATABASE_URL")
  def validate_database_url(cls, value: str) -> str:
    """
    Validates the database URL.

    Args:
      value (str): The database URL to validate.

    Returns:
      str: The validated database URL.

    Raises:
      ValueError: If the database URL is invalid.
    """
    if not value.startswith("mongodb://") and not value.startswith(
      "mongodb+srv://"
    ):
      raise ValueError("Invalid MongoDB URL")
    return value

  @model_validator(mode="after")
  def validate_sentry_non_local(self) -> "Config":
    """
    Validates the Sentry configuration for non-local environments.

    Returns:
      Config: The updated configuration.

    Raises:
      ValueError: If Sentry is not set in a deployed environment.
    """
    if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
      raise ValueError("Sentry is not set")

    return self

# Load the configuration
settings = Config()

# FastAPI app configurations
app_configs: dict[str, Any] = {"title": "App API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

# Hide OpenAPI docs in production
if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs
