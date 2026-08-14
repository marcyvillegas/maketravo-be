from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.concurrency import run_in_threadpool

from src.firebase.auth_client import FirebaseAuthClient

security = HTTPBearer()
fb_auth = FirebaseAuthClient()


async def create_session(
    credential: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    res = await run_in_threadpool(
        fb_auth.create_session, id_token=credential.credentials
    )
    return res
