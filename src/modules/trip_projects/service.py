from typing import Any

from src.modules.users.exceptions import EmailNotAvailable
from src.modules.trip_projects.models import TripProject
from src.modules.trip_projects.repositories import TripProjectRepo
from src.modules.trip_projects.schemas import CreateTripProjectRequest
from src.logging import scope_logger

logger = scope_logger()


async def create_trip_project(
    *,
    claims: dict[str, Any],
    trip_project_repo: TripProjectRepo,
    payload: CreateTripProjectRequest,
) -> TripProject | None:
    uid: str = claims["uid"]

    project = await trip_project_repo.create(
        TripProject(
            name=payload.name,
            description=payload.description,
            user_id=uid,
        )
    )

    logger.info(f"created trip project for {uid}")

    return project


async def get_trip_projects(
    *,
    trip_project_repo: TripProjectRepo,
    limit: int = 20,
    skip: int = 0,
) -> list[TripProject | None]:
    return await trip_project_repo.list_recent(limit=limit, skip=skip)
    # raise EmailNotAvailable()
