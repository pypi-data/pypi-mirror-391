"""Custom exceptions for the vLLM SDK."""

from typing import Optional


class VLLMAPIError(Exception):
    """Base exception for vLLM API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class VLLMConnectionError(VLLMAPIError):
    """Raised when connection to the API fails."""

    pass


class VLLMValidationError(VLLMAPIError):
    """Raised when request or response validation fails."""

    pass
