import re

from pydantic import EmailStr, Field, field_validator

from src.models import CustomModel

# Regular expression pattern for a strong password
STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


# Represents the schema for an authenticated user
class AuthUser(CustomModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    # Validates the password field after it has been set
    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError("Password must contain at least " "one lowercase character, " "one uppercase character, " "one digit, " "or special symbol")
        return password


# Represents the schema for JWT data
class JWTData(CustomModel):
    user_id: str = Field(alias="sub")  # Adjusted to expect a string
    is_admin: bool = False


# Represents the response schema for an access token
class AccessTokenResponse(CustomModel):
    access_token: str
    refresh_token: str


# Represents the response schema for a user
class UserResponse(CustomModel):
    email: EmailStr
