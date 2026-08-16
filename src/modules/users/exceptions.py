from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode


class UserNotFound(BaseDomainException):
    message = "There is no existing user"
    internal_code = "USER_NOT_FOUND"
    status_code = StatusCode.NOT_FOUND
