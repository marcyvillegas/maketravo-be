from typing import Annotated

from fastapi import Depends


from src.mongodb.dependencies import DatabaseDep
from src.modules.trip_projects.repositories import (
    TripProjectRepo,
    mongo_trip_project_repo,
)


# === Repo Dependency ===
def get_trip_project_repo(db: DatabaseDep) -> TripProjectRepo:
    return mongo_trip_project_repo(db)


TripProjectRepoDep = Annotated[TripProjectRepo, Depends(get_trip_project_repo)]
