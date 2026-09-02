from src.firebase.exceptions import InvalidCredential
from src.shared.exceptions.base import BaseDomainException

_TRACE_ID_EXAMPLE = "b3f1c2b0-6e3a-4b8a-9d2e-2a6c9f1e0a11"


def domain_error_response(exc: type[BaseDomainException]) -> dict:
    """Build a FastAPI `responses=` entry from a BaseDomainException subclass.

    `description` is docstring-only metadata; `internal_code`/`message` are
    what `domain_exception_handler` (global_exception.py) actually puts on
    the wire, so the example mirrors that envelope shape.
    """
    return {
        "description": exc.description or exc.message,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": exc.internal_code,
                        "message": exc.message,
                        "trace_id": _TRACE_ID_EXAMPLE,
                    },
                }
            }
        },
    }


# Every route in this module requires a valid Firebase session/ID token.
# HTTPBearer itself returns a bare 403 when the Authorization header is
# missing or malformed (no BaseDomainException involved), so it's documented
# separately from the 401s raised once the token is actually verified.
_UNAUTHENTICATED_RESPONSES = {
    403: {
        "description": "Missing or malformed `Authorization: Bearer <token>` header.",
    },
    401: domain_error_response(InvalidCredential),
}
