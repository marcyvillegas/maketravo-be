from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserData(BaseModel):
    """
    The Firebase client-SDK `User` the frontend posts as `user_data`.

    Client-supplied and therefore UNTRUSTED — anyone holding a valid ID token
    can post whatever they like here. Identity comes from the verified token;
    these fields are only a fallback for profile display values the token
    happens not to carry.
    """

    # The client SDK uses camelCase; accept that without renaming our fields.
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    uid: str | None = None
    email: EmailStr | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    photo_url: str | None = Field(default=None, alias="photoURL")


class CreateSessionRequest(BaseModel):
    """Body of POST /api/sessions."""

    user_data: UserData | None = None
