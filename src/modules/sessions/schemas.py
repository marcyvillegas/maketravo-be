from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateSessionRequest(BaseModel):
    """
    Body of POST /api/sessions.

    Client-supplied and therefore UNTRUSTED — anyone holding a valid ID token
    can post whatever they like here. Identity comes from the verified token;
    these fields are only a fallback for profile display values the token
    happens not to carry.
    """

    # The client SDK uses camelCase; accept that without renaming our fields.
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: EmailStr
    display_name: str = Field(..., alias="displayName")
    photo_url: str = Field(..., alias="photoURL")
