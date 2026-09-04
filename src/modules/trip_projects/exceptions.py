from enum import Enum

from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode


class TripProjectErrorCode(str, Enum):
    """Internal error codes returned by the trip_projects module."""

    TRIP_PROJECT_NOT_FOUND = "TRIP_PROJECT_NOT_FOUND"


class TripProjectNotFound(BaseDomainException):
    message = "There is no existing trip project"
    internal_code = TripProjectErrorCode.TRIP_PROJECT_NOT_FOUND
    status_code = StatusCode.NOT_FOUND
    description = "No `TripProject` record exists for this Firebase account."
