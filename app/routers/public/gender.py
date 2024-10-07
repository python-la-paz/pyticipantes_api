from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public
from app.models import Gender, Result, Token, UserAPI
from app.services.bl import UserProfileService

router = APIRouter()

@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[Gender]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def get_data(user: Token = Depends(get_api_key_public)):
    return UserProfileService.list_gender()