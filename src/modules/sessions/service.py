from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials

from src.modules.sessions.schemas import CreateSessionRequest
from src.modules.users.models import User
from src.modules.users.repositories import UserRepo
from src.firebase.auth_client import FirebaseAuthClient
from src.shared.cookie import _CookieProtocol, create_cookie
from src.logging import scope_logger

logger = scope_logger()

# async def get_session(
#     *,
#     response: _CookieProtocol,
#     credential: HTTPAuthorizationCredentials,
# ):


async def create_session(
    *,
    response: _CookieProtocol,
    credential: HTTPAuthorizationCredentials,
    fb_auth: FirebaseAuthClient,
    user_repo: UserRepo,
    payload: CreateSessionRequest | None = None,
) -> None:
    cookie_value, claims = await run_in_threadpool(
        fb_auth.create_session, id_token=credential.credentials
    )

    # todo: use decoded token instead n clean up

    # Never log cookie_value or credential.credentials — both are bearer
    # credentials, and anything in the logs is replayable until it expires.
    logger.info("session cookie minted")

    create_cookie(cookie=fb_auth.cookie, response=response, cookie_value=cookie_value)

    # Identity comes from the SIGNED token, never from the body. The body's
    # user_data is only consulted for display fields the token may omit.
    uid: str = claims["uid"]
    email = claims.get("email") or (payload.email if payload else None)

    if email is None:
        logger.warning(f"token for {uid} carries no email; skipping user upsert")
        return

    existing = await user_repo.get_by_uid(uid)
    if existing is None:
        await user_repo.create(
            User(
                firebase_uid=uid,
                email=email,
                display_name=claims.get("name")
                or (payload.display_name if payload else None),
                photo_url=claims.get("picture")
                or (payload.photo_url if payload else None),
            )
        )
        logger.info(f"created user record for {uid}")
    else:
        await user_repo.touch_last_seen(uid)
