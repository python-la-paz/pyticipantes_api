from fastapi.responses import JSONResponse
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from app.auth.access import get_api_key_public
from app.models import Result, Token, UserInDB
from app.models.user import User, UserAPI
from app.services import TokenPublicService, UserService
from app.services.bl import UserProfileService

router = APIRouter()


@router.get(
    "/me",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": UserAPI},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def get_data(user: Token = Depends(get_api_key_public)):
    try:
        find = UserProfileService.get_public_user(user.username)
        if not find:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=Result(message="Usuario no encontrado").model_dump(),
            )
        return find
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Token de acceso no válido")


@router.put(
    "/me",
    responses={
        status.HTTP_201_CREATED: {"model": UserAPI},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def put_data(userAPI: UserAPI, user: User = Depends(get_api_key_public)):
    userAPI.username = user.username
    ret = UserProfileService.update_user(userAPI)

    return ret
