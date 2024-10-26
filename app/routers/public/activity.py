from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public
from app.models import Result, Token, Activity
from app.services import ActivityService

router = APIRouter()

@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[Activity]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def get_activities(user: Token = Depends(get_api_key_public)):
    """Retrieve a list of activities."""
    activities = ActivityService.list()
    if not activities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No activities found.")
    return activities