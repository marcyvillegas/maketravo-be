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


# Function decorator
def handle_firebase_auth_error(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except fb_auth.ExpiredIdTokenError as e:
            raise CredentialExpired() from e
        except fb_auth.RevokedIdTokenError as e:
            raise CredentialRevoked() from e
        except fb_auth.ExpiredSessionCookieError as e:
            raise CredentialExpired() from e
        except fb_auth.RevokedSessionCookieError as e:
            raise CredentialRevoked() from e
        except fb_auth.InvalidIdTokenError as e:
            raise InvalidCredential() from e
        except fb_auth.InvalidSessionCookieError as e:
            raise InvalidCredential() from e
        except fb_auth.UserDisabledError as e:
            raise UserDisabled() from e
        except fb_auth.CertificateFetchError as e:
            raise AuthUnavailable() from e
        except fb_exceptions.FirebaseError as e:
            logger.warning(f"Unmapped Firebase error: {type(e).__name__}: {e}")
            raise AuthUnavailable() from e

    return wrapper


# Exceptions handling for HTTP response
