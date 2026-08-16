from collections.abc import Awaitable, Callable
from typing import NamedTuple, Protocol

from pymongo import DESCENDING, ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.modules.users.models import User
from src.mongodb.exceptions import handle_mongo_error
from src.mongodb.models import utcnow

COLLECTION = "users"


# === The contract / Interface ==================
class ListRecent(Protocol):

    def __call__(self, *, limit: int = 20) -> Awaitable[list[User | None]]: ...


class UserRepo(NamedTuple):

    get_by_uid: Callable[[str], Awaitable[User | None]]
    create: Callable[[User], Awaitable[User | None]]
    touch_last_seen: Callable[[str], Awaitable[User | None]]
    list_recent: ListRecent


# === User Repository ==================
def mongo_user_repo(db: AsyncDatabase) -> UserRepo:
    col = db[COLLECTION]

    @handle_mongo_error
    async def get_by_uid(uid: str) -> User | None:
        return User.from_mongo(await col.find_one({"firebase_uid": uid}))

    @handle_mongo_error
    async def create(user: User) -> User | None:
        doc = user.to_mongo()
        await col.insert_one(doc)
        return User.from_mongo(doc)

    @handle_mongo_error
    async def touch_last_seen(uid: str) -> User | None:
        return User.from_mongo(
            await col.find_one_and_update(
                {"firebase_uid": uid},
                {"$set": {"last_seen_at": utcnow()}},
                return_document=ReturnDocument.AFTER,
            )
        )

    @handle_mongo_error
    async def list_recent(*, limit: int = 20) -> list[User | None]:
        cursor = col.find().sort("created_at", DESCENDING).limit(limit)
        return [User.from_mongo(d) for d in await cursor.to_list(length=limit)]

    return UserRepo(
        get_by_uid=get_by_uid,
        create=create,
        touch_last_seen=touch_last_seen,
        list_recent=list_recent,
    )
