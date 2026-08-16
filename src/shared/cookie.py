# memoryview[int] below is only subscriptable at runtime on 3.14+; this makes
# all annotations in the module lazy strings, so it stays a checker-only type.
from __future__ import annotations

from typing import Any, Protocol
from src.firebase.constants import MAX_SESSION_TTL
from src.shared.constants import EnviromnentEnums
from src.config import settings


class CookieSettings:
    """
    ``name`` must stay ``__session`` on Firebase Hosting — it's the only cookie
    Hosting forwards to the backend.

    ``domain`` needs a leading dot to be shared across subdomains
    (``.yourdomain.com``); leave it ``None`` on localhost.

    ``samesite`` is ``lax``, not ``strict`` — strict breaks the OAuth return
    navigation. ``lax`` means the cookie rides along on top-level GET
    navigations (the provider's redirect back to us) but is withheld from
    cross-site POSTs, iframes, and background fetches, which is what blocks
    CSRF.

    ``secure`` must be False over plain HTTP locally or the browser
    silently drops the cookie.
    """

    # todo: dynamic domain per environment - dev, staging, prod

    name: str = "__session"
    domain: str | None = (
        settings.APP_DOMAIN
        if settings.ENVIRONMENT == EnviromnentEnums.PROD.value
        else None
    )
    path: str = "/"
    secure: bool = (
        True if settings.ENVIRONMENT == EnviromnentEnums.PROD.value else False
    )
    samesite: str = "lax"


# Cookie protocol
class _CookieProtocol(Protocol):
    """Structural type so the service layer doesn't import FastAPI.

    In practice this only ever receives a real ``Response``. It's kept so a
    service with real logic can be unit-tested against a fake object that
    just records the cookie it was handed.
    """

    def set_cookie(self, *args: Any, **kwargs: Any) -> None: ...
    def delete_cookie(self, *args: Any, **kwargs: Any) -> None: ...


def create_cookie(
    *, cookie: CookieSettings, response: _CookieProtocol, cookie_value: str
) -> None:

    response.set_cookie(
        key=cookie.name,
        value=cookie_value,
        max_age=int(MAX_SESSION_TTL.total_seconds()),
        httponly=True,
        secure=cookie.secure,
        samesite=cookie.samesite,
        domain=cookie.domain,
        path=cookie.path,
    )


def remove_cookie(*, cookie: CookieSettings, response: _CookieProtocol) -> None:
    response.delete_cookie(cookie.name, domain=cookie.domain, path=cookie.path)
