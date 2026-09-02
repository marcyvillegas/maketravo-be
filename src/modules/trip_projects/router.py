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
