from typing import Optional, Dict


class ApiError(Exception):
    """Legacy API error wrapper.

    Updated to align with enhanced client-side `ApiError` so downstream code can rely
    on attributes: message, code, status, error_type, details, response_headers, response_body.
    """

    def __init__(
        self,
        message: str = "",
        code: Optional[int] = None,
        status: Optional[int] = None,
        error_type: Optional[str] = None,
        details: Optional[Dict] = None,
        response_headers: Optional[Dict] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message  # ensure attribute exists
        self.code = code if code is not None else status
        self.status = status if status is not None else code
        self.error_type = error_type
        self.details = details or {}
        self.response_headers = response_headers
        self.response_body = response_body

    @classmethod
    def from_error(cls, error: Exception) -> "ApiError":
        """Convert arbitrary error into ApiError preserving rich fields when available."""
        if isinstance(error, cls):
            return error
        # If it's the newer client ApiError, just wrap its attributes
        code = getattr(error, "code", getattr(error, "status", None))
        status = getattr(error, "status", getattr(error, "code", None))
        message = getattr(error, "message", str(error))
        error_type = getattr(error, "error_type", None)
        details = getattr(error, "details", {}) or {}
        response_headers = getattr(error, "response_headers", None)
        response_body = getattr(error, "response_body", None)

        # Fallback inference from message if code/status missing
        msg_lower = message.lower()
        if code is None or status is None:
            if "404" in msg_lower or "not found" in msg_lower:
                code = code or 404
                status = status or 404
            elif "500" in msg_lower or "internal" in msg_lower:
                code = code or 500
                status = status or 500

        return cls(
            message=message,
            code=code,
            status=status,
            error_type=error_type,
            details=details,
            response_headers=response_headers,
            response_body=response_body,
        )
