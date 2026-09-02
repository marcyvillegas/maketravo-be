from datetime import datetime
from pydantic import Field
from src.mongodb.models import MongoModel, utcnow


class TripProject(MongoModel):
    name: str
    description: str | None = None
    user_id: str
    created_at: datetime = Field(default_factory=utcnow)
    last_seen_at: datetime = Field(default_factory=utcnow)
