from src.shared.exceptions.status_codes import StatusCode


class BaseDomainException(Exception):
    """The foundational parent exception for all internal system errors."""

    message: str = "An internal error occurred"
    internal_code: str = "INTERNAL_ERROR"
    status_code: int = StatusCode.INTERNAL_SERVER_ERROR
    scope: str | None = None

    # Docstring/Swagger metadata only — never sent in a response body. Use
    # `message` for the text actually returned to callers.
    description: str = ""

    def __init__(
        self,
        *,
        message: str | None = None,
        internal_code: str | None = None,
        status_code: int | None = None,
        scope: str | None = None
    ):
        if message is not None:
            self.message = message
        if internal_code is not None:
            self.internal_code = internal_code
        if status_code is not None:
            self.status_code = status_code
        if scope is not None:
            self.scope = scope

        "The super() is used to override the property while calling it. Example: raise ExpiredToken(message='Message here')"
        super().__init__(self.message)
        super().__init__(self.scope)
