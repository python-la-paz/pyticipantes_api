from typing import List

from fastapi import APIRouter, Depends, status

from app.auth.access import get_api_key_public
from app.models import Location, Result, Token
from app.services.bl import UserProfileService

router = APIRouter()


@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[Location]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def get_data(user: Token = Depends(get_api_key_public)):
    return UserProfileService.list_locations()
