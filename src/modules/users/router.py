from fastapi import APIRouter, status
from fastapi.security import HTTPBearer

from src.middleware.verify_token import VerifiedTokenClaimsDep
from src.modules.users.dependencies import UserRepoDep, ValidUserDep
from src.modules.users.exceptions import (
    EmailNotAvailable,
    UserAlreadyExists,
    UserNotFound,
)
from src.modules.users.models import User
from src.modules.users.schemas import CreateUserRequest
from src.modules.users import service
from src.shared.exceptions.openapi import (
    _UNAUTHENTICATED_RESPONSES,
    domain_error_response,
)
from src.shared.response import SuccessResponse

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/:id",
    status_code=status.HTTP_200_OK,
    summary="Get the caller's user record",
    response_model=SuccessResponse[User],
    responses={
        **_UNAUTHENTICATED_RESPONSES,
        404: domain_error_response(UserNotFound),
    },
)
async def get_user(
    claims: VerifiedTokenClaimsDep,
    user: ValidUserDep,
):
    """
    Fetch the `User` document tied to the caller's verified Firebase UID.

    **Auth:** `Authorization: Bearer <Firebase ID token>` required.

    **Returns:** `{"success": true, "data": <User>}` — the stored `User`
    record (`_id`, `firebase_uid`, `email`, `display_name`, `photo_url`,
    `created_at`, `last_seen_at`).
    """
    return SuccessResponse(data=user)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a user record for the caller",
    response_model=SuccessResponse[User],
    responses={
        **_UNAUTHENTICATED_RESPONSES,
        400: domain_error_response(EmailNotAvailable),
        409: domain_error_response(UserAlreadyExists),
    },
)
async def create_user(
    claims: VerifiedTokenClaimsDep,
    user_repo: UserRepoDep,
    payload: CreateUserRequest | None = None,
):
    """
    Create the local `User` record for the caller's verified Firebase UID.

    **Auth:** `Authorization: Bearer <Firebase ID token>` required.

    **Identity source:** `firebase_uid`, `email`, `display_name`, and
    `photo_url` are read from the *verified token claims* first. The
    optional request body fields are only used as a fallback for
    `email` / `display_name` / `photo_url` when the token doesn't carry
    them — they are otherwise untrusted and never used to establish
    identity.

    **Body:** optional. Example:
    ```json
    {
      "email": "jane@example.com",
      "displayName": "Jane Doe",
      "photoURL": "https://example.com/jane.png"
    }
    ```

    **Returns:** `{"success": true, "data": <User>}` — the newly created
    `User` record.
    """
    user = await service.create_user(
        claims=claims, user_repo=user_repo, payload=payload
    )
    return SuccessResponse(data=user)
