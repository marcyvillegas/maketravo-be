from enum import IntEnum


class StatusCode(IntEnum):
    """HTTP status codes returned by the API."""

    # --- 2xx Success ---
    OK = 200  # Standard response for a successful request.
    CREATED = 201  # Resource was created; return with the new resource.
    ACCEPTED = 202  # Request accepted for processing, not yet finished.
    NO_CONTENT = 204  # Success, but there is no body to return (e.g. DELETE).

    # --- 3xx Redirection ---
    MOVED_PERMANENTLY = 301  # Resource has a new permanent URL.
    FOUND = 302  # Resource is temporarily at a different URL.
    NOT_MODIFIED = 304  # Cached copy is still valid; no body sent.

    # --- 4xx Client Error ---
    BAD_REQUEST = 400  # Malformed request the server refuses to process.
    UNAUTHORIZED = 401  # No valid credentials; caller must authenticate.
    FORBIDDEN = 403  # Authenticated, but not allowed to do this.
    NOT_FOUND = 404  # No resource exists at this path.
    METHOD_NOT_ALLOWED = 405  # Path exists, but not for this HTTP method.
    CONFLICT = 409  # Clashes with current state (e.g. duplicate email).
    GONE = 410  # Resource existed before but was permanently removed.
    PAYLOAD_TOO_LARGE = 413  # Body exceeds the size the server accepts.
    UNSUPPORTED_MEDIA_TYPE = 415  # Content-Type is not one the server handles.
    UNPROCESSABLE_ENTITY = 422  # Well-formed but fails validation (Pydantic default).
    TOO_MANY_REQUESTS = 429  # Rate limit exceeded; caller should back off.

    # --- 5xx Server Error ---
    INTERNAL_SERVER_ERROR = 500  # Unhandled failure on our side.
    NOT_IMPLEMENTED = 501  # Endpoint is not built yet.
    BAD_GATEWAY = 502  # Invalid response from an upstream service.
    SERVICE_UNAVAILABLE = 503  # Temporarily down or overloaded; retry later.
    GATEWAY_TIMEOUT = 504  # Upstream service did not respond in time.
