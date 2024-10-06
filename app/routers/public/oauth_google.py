import requests
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from app.auth.access import get_api_key_public
from app.models import Result, Token, UserInDB
from app.services import TokenPublicService, UserService

router = APIRouter()


@router.get("/login")
async def login_public(request: Request):
    token = request.headers.get("Authorization")
    if token is not None:
        result = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": token},
        )
        if result.status_code == 200:
            data = result.json()
            userDB = UserInDB(
                username=data.get("email"),
                email=data.get("email"),
                picture=data.get("picture"),
                given_name=data.get("given_name"),
                family_name=data.get("family_name"),
                disabled=False,
            )
            ret = UserService.insert_or_update_user(userDB)
            if ret.disabled == True:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario no disponible.",
                )
            generated, token = TokenPublicService.create(
                Token(username=ret.username, token="")
            )
            return {"token": token}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )


@router.get("/logout", response_model=Result)
async def logout_public(user: Token = Depends(get_api_key_public)):
    TokenPublicService.delete_by_jti(jti=user.jti)
    return Result(message="Logout Success")


@router.options("/logout", response_model=Result)
async def logout_public_options(user: Token = Depends(get_api_key_public)):
    TokenPublicService.delete_by_jti(jti=user.jti)
    return Result(message="Logout Success")
