from fastapi import APIRouter, status

from src.middleware.verify_token import VerifiedTokenClaimsDep
from src.modules.trip_projects.dependencies import TripProjectRepoDep
from src.modules.trip_projects.models import TripProject
from src.modules.trip_projects.schemas import CreateTripProjectRequest
from src.modules.trip_projects import service
from src.shared.exceptions.openapi import _UNAUTHENTICATED_RESPONSES
from src.shared.response import SuccessResponse

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a trip project for the caller",
    response_model=SuccessResponse[TripProject],
    responses={
        **_UNAUTHENTICATED_RESPONSES,
    },
)
async def create_trip_project(
    claims: VerifiedTokenClaimsDep,
    trip_project_repo: TripProjectRepoDep,
    payload: CreateTripProjectRequest,
):
    """
    Create a `TripProject` owned by the caller's verified Firebase UID.

    **Auth:** `Authorization: Bearer <Firebase ID token>` required.

    **Identity source:** `user_id` is read from the *verified token claims*,
    never from the request body.

    **Returns:** `{"success": true, "data": <TripProject>}` — the newly
    created `TripProject` record.
    """
    project = await service.create_trip_project(
        claims=claims, trip_project_repo=trip_project_repo, payload=payload
    )
    return SuccessResponse(data=project)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List trip projects",
    response_model=SuccessResponse[list[TripProject | None]],
    responses={
        **_UNAUTHENTICATED_RESPONSES,
    },
)
async def get_trip_projects(
    claims: VerifiedTokenClaimsDep,
    trip_project_repo: TripProjectRepoDep,
    limit: int = 20,
    skip: int = 0,
):
    """
    List `TripProject` records, most recently created first.

    **Auth:** `Authorization: Bearer <Firebase ID token>` required.

    **Pagination:** `limit` (page size, default 20) and `skip` (offset,
    default 0).

    **Returns:** `{"success": true, "data": [<TripProject>, ...]}`.
    """
    projects = await service.get_trip_projects(
        trip_project_repo=trip_project_repo, limit=limit, skip=skip
    )
    return SuccessResponse(data=projects)
