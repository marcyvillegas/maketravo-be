# src/database/models.py

from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field


def utcnow() -> datetime:
    """
    Always timezone-aware. Never use datetime.utcnow() — despite the name it
    returns a NAIVE datetime, which is a long-standing footgun and is
    deprecated in modern Python.
    """
    return datetime.now(timezone.utc)


class MongoModel(BaseModel):
    """Shared base. Handles the _id ↔ id translation once."""

    model_config = ConfigDict(populate_by_name=True)

    # Mongo calls it "_id"; Python can't use a leading underscore as a normal
    # field name, and our API should expose "id". alias= bridges the two.
    id: str | None = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, doc: dict | None):
        """Document → model. The only place ObjectId becomes a string."""
        if doc is None:
            return None
        doc = dict(doc)  # copy — don't mutate the driver's dict
        if isinstance(doc.get("_id"), ObjectId):
            doc["_id"] = str(doc["_id"])
        return cls.model_validate(doc)

    def to_mongo(self) -> dict:
        """Model → document. Drop id — Mongo assigns _id on insert."""
        return self.model_dump(by_alias=True, exclude_none=True, exclude={"id"})
