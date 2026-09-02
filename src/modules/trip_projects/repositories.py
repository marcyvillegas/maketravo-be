from collections.abc import Awaitable, Callable
from typing import NamedTuple, Protocol

from pymongo import DESCENDING, ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from src.modules.trip_projects.models import TripProject
from src.mongodb.exceptions import handle_mongo_error
from src.mongodb.models import utcnow

COLLECTION = "trip_projects"


# === The contract / Interface ==================
class ListRecent(Protocol):

    def __call__(self, *, limit: int = 20) -> Awaitable[list[TripProject | None]]: ...


class TripProjectRepo(NamedTuple):

    get_by_uid: Callable[[str], Awaitable[TripProject | None]]
    create: Callable[[TripProject], Awaitable[TripProject | None]]
    touch_last_seen: Callable[[str], Awaitable[TripProject | None]]
    list_recent: ListRecent


# === Repository ==================
def mongo_trip_project_repo(db: AsyncDatabase) -> TripProjectRepo:
    col = db[COLLECTION]

    @handle_mongo_error
    async def get_by_uid(uid: str) -> TripProject | None:
        return TripProject.from_mongo(await col.find_one({"_id": uid}))

    @handle_mongo_error
    async def create(user: TripProject) -> TripProject | None:
        doc = user.to_mongo()
        await col.insert_one(doc)
        return TripProject.from_mongo(doc)

    @handle_mongo_error
    async def touch_last_seen(uid: str) -> TripProject | None:
        return TripProject.from_mongo(
            await col.find_one_and_update(
                {"_id": uid},
                {"$set": {"last_seen_at": utcnow()}},
                return_document=ReturnDocument.AFTER,
            )
        )

    @handle_mongo_error
    async def list_recent(*, limit: int = 20) -> list[TripProject | None]:
        cursor = col.find().sort("created_at", DESCENDING).limit(limit)
        return [TripProject.from_mongo(d) for d in await cursor.to_list(length=limit)]

    return TripProjectRepo(
        get_by_uid=get_by_uid,
        create=create,
        touch_last_seen=touch_last_seen,
        list_recent=list_recent,
    )
