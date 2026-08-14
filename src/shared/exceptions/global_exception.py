"""
Global Exception Registry

This handles global exceptions seamlessly.
"""

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.logging import scope_logger
from src.shared.exceptions.base import BaseDomainException
from src.shared.exceptions.error_codes import GlobalErrorCode
from src.shared.exceptions.error_messages import GlobalErrorMessage
from src.shared.exceptions.status_codes import StatusCode

logger = scope_logger()


async def domain_exception_handler(request: Request, exc: BaseDomainException):
    """
    Expected failures raised by our own code. These carry their own status code
    and a message that is safe to show the caller.
    """
    logger.warning(f"{exc.internal_code}: {exc}")

    return JSONResponse(
        status_code=int(exc.status_code),
        content={
            "success": False,
            "error": {
                "code": exc.internal_code,
                "message": exc.message,
            },
        },
    )


async def production_safety_net_handler(request: Request, exc: Exception):
    """
    Catch-all mechanism preventing runtime infrastructure or Python script errors
    (e.g., Unhandled KeyErrors, ValueErrors) from exposing system traces to consumers.
    """
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
    app.add_exception_handler(BaseDomainException, domain_exception_handler)
    app.add_exception_handler(Exception, production_safety_net_handler)
