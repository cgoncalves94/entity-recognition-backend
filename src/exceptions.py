from typing import Any

from fastapi import HTTPException, status


class DetailedHTTPException(HTTPException):
    """
    Custom HTTP exception class that provides detailed information about the exception.
    """

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """
        Initializes the DetailedHTTPException object.

        Args:
          **kwargs: Additional keyword arguments to be passed to the parent class.
        """
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    """
    Exception class for permission denied errors.
    """

    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    """
    Exception class for resource not found errors.
    """

    STATUS_CODE = status.HTTP_404_NOT_FOUND


class BadRequest(DetailedHTTPException):
    """
    Exception class for bad request errors.
    """

    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"


class NotAuthenticated(DetailedHTTPException):
    """
    Exception class for unauthenticated user errors.
    """

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        """
        Initializes the NotAuthenticated object.
        """
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
