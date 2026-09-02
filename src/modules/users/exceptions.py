from enum import Enum

from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode


class UserErrorCode(str, Enum):
    """Internal error codes returned by the users module."""

    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    EMAIL_NOT_AVAILABLE = "EMAIL_NOT_AVAILABLE"


class UserNotFound(BaseDomainException):
    message = "There is no existing user"
    internal_code = UserErrorCode.USER_NOT_FOUND
    status_code = StatusCode.NOT_FOUND
    description = "No local `User` record exists for this Firebase account."


class UserAlreadyExists(BaseDomainException):
    message = "A user already exists for this account"
    internal_code = UserErrorCode.USER_ALREADY_EXISTS
    status_code = StatusCode.CONFLICT
    description = "A `User` record already exists for this Firebase UID."


class EmailNotAvailable(BaseDomainException):
    message = "No email is available for this account"
    internal_code = UserErrorCode.EMAIL_NOT_AVAILABLE
    status_code = StatusCode.BAD_REQUEST
    description = (
        "Verified token carries no email and none was supplied in the "
        "request body either."
    )
