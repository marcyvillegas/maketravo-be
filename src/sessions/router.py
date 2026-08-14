from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.sessions import service as sessions_service

router = APIRouter()
security = HTTPBearer()


@router.post("")
async def create_session(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return await sessions_service.create_session(credential=credential)
