import functools

from src.logging import scope_logger

from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode
from firebase_admin import auth as fb_auth
from firebase_admin import exceptions as fb_exceptions

logger = scope_logger("src.firebase.auth_client")


# Exception classes
class CredentialExpired(BaseDomainException):
    message = "Session expired"
    internal_code = "AUTH_SESSION_EXPIRED"
    status_code = StatusCode.UNAUTHORIZED


class CredentialRevoked(BaseDomainException):
    message = "Session was revoked"
    internal_code = "AUTH_SESSION_REVOKED"
    status_code = StatusCode.UNAUTHORIZED


class InvalidCredential(BaseDomainException):
    message = "Invalid Token"
    internal_code = "AUTH_INVALID_TOKEN"
    status_code = StatusCode.UNAUTHORIZED


class UserDisabled(BaseDomainException):
    message = "User account is disabled"
    internal_code = "AUTH_USER_DISABLED"
    status_code = StatusCode.FORBIDDEN


class AuthUnavailable(BaseDomainException):
    message = "Authentication is temporarily unavailable"
    internal_code = "AUTH_UNAVAILABLE"
    status_code = StatusCode.SERVICE_UNAVAILABLE


class StaleSignIn(BaseDomainException):
    """ID token is valid but the sign-in behind it is too old"""

    message = "Please sign in again"
    internal_code = "AUTH_STALE_SIGN_IN"
    status_code = StatusCode.UNAUTHORIZED


_ERROR_MAP: dict[type[fb_exceptions.FirebaseError], type[BaseDomainException]] = {
    fb_auth.ExpiredIdTokenError: CredentialExpired,
    fb_auth.RevokedIdTokenError: CredentialRevoked,
    fb_auth.ExpiredSessionCookieError: CredentialExpired,
    fb_auth.RevokedSessionCookieError: CredentialRevoked,
    fb_auth.InvalidIdTokenError: InvalidCredential,
    fb_auth.InvalidSessionCookieError: InvalidCredential,
    fb_auth.UserDisabledError: UserDisabled,
    fb_auth.CertificateFetchError: AuthUnavailable,
}


def _to_domain_exception(e: fb_exceptions.FirebaseError) -> BaseDomainException:
    """Resolve a Firebase error to its nearest mapped domain exception.

    type(e).__mro__ is SomeClass.__mro__

    __mro__ returns a tuple of ancestors of that class. Thus, looping and checking if
    an ancestral class is in the _ERROR_MAP dict. It uses a child-first-then-parent
    arrangement

    e.g.  UserDisabledError (the needed exception) -> FirebaseError (parent class)
    """

    scope = "src.firebase.auth_client"

    for exception_class in type(e).__mro__:
        domain_exc = _ERROR_MAP.get(exception_class)
        if domain_exc is not None:
            return domain_exc(scope=scope)

    logger.warning(f"Unmapped Firebase error: {type(e).__name__}: {e}")
    return AuthUnavailable(scope=scope)


# Function decorator
def handle_firebase_auth_error(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except fb_exceptions.FirebaseError as e:
            raise _to_domain_exception(e) from e

    return wrapper
