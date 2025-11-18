"""Error classes for the Bluma SDK"""

from typing import Any, Dict, Optional


class BlumaError(Exception):
    """Base error class for all Bluma SDK errors"""

    pass


class APIError(BlumaError):
    """API error with status code and error details"""

    def __init__(self, status: int, error_response: Dict[str, Any]) -> None:
        error_data = error_response.get("error", {})
        self.status = status
        self.type = error_data.get("type", "api_error")
        self.title = error_data.get("title", "API Error")
        self.detail = error_data.get("detail", error_response.get("message", "An API error occurred"))
        super().__init__(self.detail)


class ValidationError(APIError):
    """Validation error (400)"""

    def __init__(self, status: int, error_response: Dict[str, Any]) -> None:
        super().__init__(status, error_response)
        metadata = error_response.get("error", {}).get("metadata", {})
        self.field: Optional[str] = metadata.get("field")


class AuthenticationError(APIError):
    """Authentication error (401)"""

    pass


class InsufficientCreditsError(APIError):
    """Insufficient credits error (402)"""

    def __init__(self, status: int, error_response: Dict[str, Any]) -> None:
        super().__init__(status, error_response)
        metadata = error_response.get("error", {}).get("metadata", {})
        self.credits_required: Optional[int] = metadata.get("credits_required")
        self.credits_available: Optional[int] = metadata.get("credits_available")


class ForbiddenError(APIError):
    """Forbidden error (403)"""

    pass


class NotFoundError(APIError):
    """Resource not found error (404)"""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded error (429)"""

    def __init__(self, status: int, error_response: Dict[str, Any], retry_after: Optional[str] = None) -> None:
        super().__init__(status, error_response)
        self.retry_after = int(retry_after) if retry_after else 60


class ServerError(APIError):
    """Server error (5xx)"""

    pass


class NetworkError(BlumaError):
    """Network or timeout error"""

    def __init__(self, original_error: Exception) -> None:
        self.original_error = original_error
        super().__init__(f"Network error: {str(original_error)}")
