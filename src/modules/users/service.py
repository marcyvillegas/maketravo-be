from typing import Any

from src.modules.users.exceptions import EmailNotAvailable, UserAlreadyExists
from src.modules.users.models import User
from src.modules.users.repositories import UserRepo
from src.modules.users.schemas import CreateUserRequest
from src.logging import scope_logger

logger = scope_logger()


async def create_user(
    *,
    claims: dict[str, Any],
    user_repo: UserRepo,
    payload: CreateUserRequest | None = None,
) -> User | None:
    # Identity comes from the SIGNED token, never from the body. The body's
    # user_data is only consulted for display fields the token may omit.
    uid: str = claims["uid"]
    email = claims.get("email") or (payload.email if payload else None)

    if email is None:
        raise EmailNotAvailable()

    if await user_repo.get_by_uid(uid) is not None:
        raise UserAlreadyExists()

    user = await user_repo.create(
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

    return user
