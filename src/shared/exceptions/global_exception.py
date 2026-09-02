"""
Global Exception Registry

This handles global exceptions seamlessly.
"""

import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.logging import scope_logger
from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.error_codes import GlobalErrorCode
from src.shared.exceptions.error_messages import GlobalErrorMessage
from src.shared.exceptions.status_codes import StatusCode


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPExceptions raised by Starlette/FastAPI itself — e.g. HTTPBearer's
    401 "Not authenticated" when the Authorization header is absent —
    bypass our BaseDomainException hierarchy entirely. Starlette special-
    cases HTTPException ahead of any handler registered on the bare
    Exception class, so unless this is registered too, those responses
    leak out as Starlette's own `{"detail": ...}` shape instead of our
    envelope.
    """

    logger = scope_logger()

    code = (
        GlobalErrorCode.AUTH_MISSING_TOKEN
        if exc.detail == "Not authenticated"
        else GlobalErrorCode.HTTP_EXCEPTION
    )

    trace_id = str(uuid.uuid4())
    logger.warning(f"[Trace ID: {trace_id}] {code.value}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code.value,
                "message": exc.detail,
                "trace_id": trace_id,
            },
        },
        headers=exc.headers,
    )


async def domain_exception_handler(request: Request, exc: BaseDomainException):
    """
    Expected failures raised by our own code. These carry their own status code
    and a message that is safe to show the caller.
    """

    logger = scope_logger(exc.scope)

    trace_id = str(uuid.uuid4())
    logger.error(
        f"[Trace ID: {trace_id}] {exc.internal_code}: {exc}",
    )

    return JSONResponse(
        status_code=int(exc.status_code),
        content={
            "success": False,
            "error": {
                "code": exc.internal_code,
                "message": exc.message,
                "trace_id": trace_id,
            },
        },
    )


async def production_safety_net_handler(request: Request, exc: Exception):
    """
    Catch-all mechanism preventing runtime infrastructure or Python script errors
    (e.g., Unhandled KeyErrors, ValueErrors) from exposing system traces to consumers.
    """

    logger = scope_logger()

    trace_id = str(uuid.uuid4())
    logger.critical(
        f"Unhandled critical crash [Trace ID: {trace_id}]: {exc}", exc_info=True
    )

    return JSONResponse(
        status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
        content={
            "success": False,
            "error": {
                "code": GlobalErrorCode.INTERNAL_SERVER_ERROR.value,
                "message": GlobalErrorMessage.UNEXPECTED_INTERNAL_ERROR.value,
                "trace_id": trace_id,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Called from main.py — keeps the import pointing one way only."""
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(BaseDomainException, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, production_safety_net_handler)
