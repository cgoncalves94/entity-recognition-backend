from typing import Any, Optional

from pydantic_settings import BaseSettings
from pydantic import validator, MongoDsn

from constants import Environment

class Config(BaseSettings):
    DATABASE_URL: str
    DATABASE_NAME: str  
    SITE_DOMAIN: str = "myapp.com"
    ENVIRONMENT: Environment = Environment.PRODUCTION
    SENTRY_DSN: Optional[str] = None
    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: Optional[str] = None
    CORS_HEADERS: list[str]
    APP_VERSION: str = "1"

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("mongodb://") and not value.startswith("mongodb+srv://"):
            raise ValueError("Invalid MongoDB URL")
        return value

    @validator("SENTRY_DSN", pre=True, always=True)
    def validate_sentry_non_local(cls, value: str, values) -> str:
        if values.get("ENVIRONMENT").is_deployed and not value:
            raise ValueError("Sentry DSN must be set in deployed environments")
        return value
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields


settings = Config()

app_configs: dict[str, Any] = {"title": "App API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # Optionally hide docs in production
