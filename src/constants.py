from enum import Enum


class Environment(str, Enum):
    """
    Enum class representing different environments.
    """

    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        """
        Check if the environment is a debug environment.
        """
        return self in (self.LOCAL, self.STAGING, self.TESTING)

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
