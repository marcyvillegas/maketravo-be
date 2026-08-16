from typing import Annotated

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase


def get_database(request: Request) -> AsyncDatabase:
    return request.app.state.mongo.db


DatabaseDep = Annotated[AsyncDatabase, Depends(get_database)]
