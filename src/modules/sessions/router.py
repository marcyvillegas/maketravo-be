from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.firebase.dependencies import FirebaseAuthDep
from src.modules.sessions.schemas import CreateSessionRequest
from src.modules.users.dependencies import UserRepoDep
from src.modules.sessions import service as sessions_service
from src.logging import scope_logger

router = APIRouter()
security = HTTPBearer()

logger = scope_logger()


# @router.get("", status_code=status.HTTP_204_NO_CONTENT)
# def get_session():
#     return


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def create_session(
    request: Request,
    response: Response,
    credential: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    fb_auth: FirebaseAuthDep,
    user_repo: UserRepoDep,
    payload: CreateSessionRequest | None = None,
) -> None:

    logger.info(f"create_session from {request.client.host if request.client else '?'}")

    await sessions_service.create_session(
        response=response,
        credential=credential,
        fb_auth=fb_auth,
        user_repo=user_repo,
        payload=payload,
    )
