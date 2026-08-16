"""
FastAPI dependency providers for Firebase.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.firebase.auth_client import FirebaseAuthClient


@lru_cache
def get_firebase_auth() -> FirebaseAuthClient:
    """
    One client per process — building it initialises the Firebase app, so it is
    cached rather than rebuilt per request. Override this in tests via
    ``app.dependency_overrides[get_firebase_auth]``.
    """
    return FirebaseAuthClient()


FirebaseAuthDep = Annotated[FirebaseAuthClient, Depends(get_firebase_auth)]
