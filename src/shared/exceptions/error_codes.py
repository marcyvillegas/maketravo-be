from enum import Enum


class GlobalErrorCode(Enum):
    """Global HTTP error message returned by the API."""

    # 5xx
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
