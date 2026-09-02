from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.firebase.dependencies import FirebaseAuthDep

security = HTTPBearer()


async def get_verified_token_claims(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    firebase_auth: FirebaseAuthDep,
) -> dict[str, Any]:
    return firebase_auth.verify_id_token(credentials.credentials)


VerifiedTokenClaimsDep = Annotated[dict[str, Any], Depends(get_verified_token_claims)]
