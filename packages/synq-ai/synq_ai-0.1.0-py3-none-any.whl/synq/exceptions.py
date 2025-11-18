"""Exception classes for Synq SDK."""


class SynqError(Exception):
    """Base exception for all Synq SDK errors."""
    pass


class SynqAPIError(SynqError):
    """Raised when the Synq API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class SynqConnectionError(SynqError):
    """Raised when connection to Synq API fails."""
    pass


class SynqValidationError(SynqError):
    """Raised when input validation fails."""
    pass

