from enum import Enum


class GlobalErrorCode(Enum):
    """Global HTTP error message returned by the API."""

    # 5xx
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

    # Raised by Starlette/FastAPI itself rather than our own domain code.
    HTTP_EXCEPTION = "HTTP_EXCEPTION"

    # HTTPBearer's own 403 when the Authorization header is absent/malformed.
    AUTH_MISSING_TOKEN = "AUTH_MISSING_TOKEN"
