from datetime import datetime
from pydantic import EmailStr, Field
from src.mongodb.models import MongoModel, utcnow


class User(MongoModel):
    firebase_uid: str  # the join key to Firebase Auth
    email: EmailStr
    display_name: str | None = None
    photo_url: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    last_seen_at: datetime = Field(default_factory=utcnow)
