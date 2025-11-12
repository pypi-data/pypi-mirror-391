class ResourceNotFoundError(Exception):
    """Exception raised when a requested resource is not found."""

    msg: str


class UnauthorizedError(Exception):
    """Exception raised when authentication fails or is missing."""

    msg: str


class ServerError(Exception):
    """Exception raised when the server returns an error response."""

    msg: str


class ServerTimeoutError(Exception):
    """Exception raised when the server times out."""

    msg: str
