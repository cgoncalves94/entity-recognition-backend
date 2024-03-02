from pydantic_settings import BaseSettings

class AuthConfig(BaseSettings):
  """
  Configuration class for authentication settings.
  """

  JWT_ALG: str
  JWT_SECRET: str
  JWT_EXP: int = 5  # minutes

  REFRESH_TOKEN_KEY: str = "refreshToken"
  REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days

  SECURE_COOKIES: bool = True

  class Config:
    env_file = ".env"
    extra = "allow"  

# Create an instance of AuthConfig
auth_config = AuthConfig()
