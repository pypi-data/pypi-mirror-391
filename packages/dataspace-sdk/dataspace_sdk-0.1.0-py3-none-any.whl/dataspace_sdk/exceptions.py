"""Custom exceptions for DataSpace SDK."""


class DataSpaceAPIError(Exception):
    """Base exception for DataSpace API errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class DataSpaceAuthError(DataSpaceAPIError):
    """Exception raised for authentication errors."""

    pass


class DataSpaceNotFoundError(DataSpaceAPIError):
    """Exception raised when a resource is not found."""

    pass


class DataSpaceValidationError(DataSpaceAPIError):
    """Exception raised for validation errors."""

    pass
