# src/database/dependencies.py

from typing import Annotated

from fastapi import Depends

from src.modules.users.models import User
from src.modules.users.exceptions import UserNotFound
from src.mongodb.dependencies import DatabaseDep
from src.modules.users.repositories import UserRepo, mongo_user_repo


# === User Repo Dependency ===
def get_user_repo(db: DatabaseDep) -> UserRepo:
    return mongo_user_repo(db)


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]


# === User Methods Dependencies ===
async def get_valid_user(*, user_repo: UserRepoDep, id: str) -> User:

    user = await user_repo.get_by_uid(id)

    if user is None:
        raise UserNotFound()

    return user


ValidUserDep = Annotated[User, Depends(get_valid_user)]
