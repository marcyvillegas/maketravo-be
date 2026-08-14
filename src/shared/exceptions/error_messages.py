from enum import Enum


class GlobalErrorMessage(Enum):
    """Global HTTP error message returned by the API."""

    UNEXPECTED_INTERNAL_ERROR = "An unexpected error occurred"
