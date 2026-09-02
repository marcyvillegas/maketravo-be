from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Envelope for every successful response — mirrors the error envelope's
    `{"success": false, "error": {...}}` shape from global_exception.py."""

    success: bool = True
    data: T
