from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from app.auth.access import get_actual_user, get_api_key
from app.models.result import Result
from app.models.token import Token, TokenUser
from app.models.user import UserInDB
from app.services.token import TokenService
from app.services.token_public import TokenPublicService
from app.utils import PyObjectId

router = APIRouter()


@router.get("", response_model=List[Token], status_code=status.HTTP_200_OK)
async def get_token(user: UserInDB = Depends(get_actual_user), q: Optional[str] = None):
    search = Token(jti="", username=user.username)
    if q is not None:
        search.jti = q
        tokens = TokenService.search(item=search)
    else:
        tokens = TokenService.get(search.username)
    return tokens


@router.post("", response_model=TokenUser, status_code=status.HTTP_201_CREATED)
async def post_token(user: UserInDB = Depends(get_actual_user)):
    item = Token(jti="", username=user.username)
    item.username_insert = user.username
    token = TokenService.create(item)
    token_mirror = Token(token=token.token, jti=token.jti, username=user.username)
    mirror =TokenPublicService.create_mirror(token_mirror)
    return token


@router.delete(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_204_NO_CONTENT: {"model": None},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def delete_token(jti: str, user: UserInDB = Depends(get_actual_user)):
    item = Token(jti=jti, username=user.username)
    ret = TokenService.get_by_jti_and_username(jti, user.username)
    if ret is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Result(message="Token not Found").model_dump(),
        )
    item.id = ret.id
    item.username_update = user.username
    TokenService.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/echo", response_model=str, status_code=status.HTTP_200_OK)
async def echo_test_token(
    q: Optional[str] = None, user: UserInDB = Depends(get_api_key)
):
    return f"{user.username} says: '{q}'"
