from enum import Enum


class Environment(str, Enum):
    """
    Enum class representing different environments.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def is_debug(self):
        """
        Check if the environment is a debug environment.
        """
        return self in (self.DEVELOPMENT, self.TESTING, self.STAGING)

    @property
    def is_testing(self):
        """
        Check if the environment is a testing environment.
        """
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        """
        Check if the environment is a deployed environment.
        """
        return self in (self.STAGING, self.PRODUCTION)
