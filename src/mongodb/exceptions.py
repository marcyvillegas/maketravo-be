import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from bson.errors import InvalidId
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    ExecutionTimeout,
    NetworkTimeout,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from src.logging import scope_logger
from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.status_codes import StatusCode

logger = scope_logger()


class DatabaseUnavailable(BaseDomainException):
    message = "Service is temporarily unavailable"
    internal_code = "DB_UNAVAILABLE"
    status_code = StatusCode.SERVICE_UNAVAILABLE  # 503


class DatabaseTimeout(BaseDomainException):
    message = "The request took too long"
    internal_code = "DB_TIMEOUT"
    status_code = StatusCode.GATEWAY_TIMEOUT  # 504


class DuplicateResource(BaseDomainException):
    message = "That record already exists"
    internal_code = "DB_DUPLICATE_KEY"
    status_code = StatusCode.CONFLICT  # 409


class InvalidIdentifier(BaseDomainException):
    message = "Invalid identifier"
    internal_code = "DB_INVALID_ID"
    status_code = StatusCode.BAD_REQUEST  # 400


class DatabaseError(BaseDomainException):
    message = "Something went wrong"
    internal_code = "DB_ERROR"
    status_code = StatusCode.INTERNAL_SERVER_ERROR  # 500


def _duplicate_fields(exc: DuplicateKeyError) -> str:

    pattern = (exc.details or {}).get("keyPattern") or {}
    return ", ".join(pattern.keys()) or "field"


_ERROR_MAP: dict[type[Exception], tuple[type[BaseDomainException], int]] = {
    # --- caller's fault: expected, low severity ---
    DuplicateKeyError: (DuplicateResource, logging.INFO),
    InvalidId: (InvalidIdentifier, logging.INFO),
    # --- transient ---
    NetworkTimeout: (DatabaseTimeout, logging.WARNING),
    ExecutionTimeout: (DatabaseTimeout, logging.WARNING),
    # --- ours / infrastructure ---
    ServerSelectionTimeoutError: (DatabaseUnavailable, logging.ERROR),
    ConnectionFailure: (DatabaseUnavailable, logging.ERROR),
    OperationFailure: (DatabaseError, logging.ERROR),
    PyMongoError: (DatabaseError, logging.ERROR),
}


def _to_domain_exception(e: Exception, where: str) -> BaseDomainException:
    for exception_class in type(e).__mro__:
        mapped = _ERROR_MAP.get(exception_class)
        if mapped is None:
            continue

        domain_exc, level = mapped

        if isinstance(e, DuplicateKeyError):
            fields = _duplicate_fields(e)
            logger.log(level, f"Duplicate key on {fields} in {where}")
            return domain_exc(
                message=f"A record with this {fields} already exists",
            )

        code = f" (code={e.code})" if isinstance(e, OperationFailure) else ""
        logger.log(level, f"{type(e).__name__} in {where}{code}: {e}")
        return domain_exc()

    logger.exception(f"Unmapped database error in {where}: {type(e).__name__}")
    return DatabaseError()


P = ParamSpec("P")  # carries the wrapped function's parameters
R = TypeVar("R")  # carries its return type

AsyncFn = Callable[P, Coroutine[Any, Any, R]]


def handle_mongo_error(func: AsyncFn[P, R]) -> AsyncFn[P, R]:

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)

        except (PyMongoError, InvalidId) as e:
            raise _to_domain_exception(e, func.__qualname__) from e

    return wrapper
