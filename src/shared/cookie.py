from dataclasses import dataclass
from typing import Any, Protocol
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
    "Protocol is used to make it modular"

    def set_cookie(self, **kwargs: Any) -> Any: ...
    def delete_cookie(self, *args: Any, **kwargs: Any) -> Any: ...


def create_cookie(
    *,
    cookie: CookieSettings,
    response: _CookieProtocol,
    session_max_age: int,
    cookie_value: str
) -> None:

    response.set_cookie(
        key=cookie.name,
        value=cookie_value,
        max_age=session_max_age,
        httponly=True,
        secure=cookie.secure,
        samesite=cookie.samesite,
        domain=cookie.domain,
        path=cookie.path,
    )


def remove_cookie(*, cookie: CookieSettings, response: _CookieProtocol) -> None:
    response.delete_cookie(cookie.name, domain=cookie.domain, path=cookie.path)
