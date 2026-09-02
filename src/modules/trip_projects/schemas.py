from pydantic import BaseModel


class CreateTripProjectRequest(BaseModel):

    name: str
    description: str | None = None
