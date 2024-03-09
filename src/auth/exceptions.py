from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated, PermissionDenied


class AuthRequired(NotAuthenticated):
    """Exception raised when authentication is required."""

    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    """Exception raised when authorization fails."""

    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidToken(NotAuthenticated):
    """Exception raised when an invalid token is encountered."""

    DETAIL = ErrorCode.INVALID_TOKEN


class InvalidCredentials(NotAuthenticated):
    """Exception raised when invalid credentials are provided."""

    DETAIL = ErrorCode.INVALID_CREDENTIALS


class EmailTaken(BadRequest):
    """Exception raised when an email is already taken."""

    DETAIL = ErrorCode.EMAIL_TAKEN


class RefreshTokenNotValid(NotAuthenticated):
    """Exception raised when a refresh token is not valid."""

    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID
