import json

from fastapi import Request, Security, status
from fastapi.exceptions import HTTPException
from fastapi.security.api_key import APIKeyHeader
from jose import JWSError, jws

from app.core import configuration
from app.models.token import Token
from app.services import TokenPublicService
from app.models.user import UserInDB
from app.services.token import TokenService
from app.services.user import UserService

SECRET = configuration.APP_SECRET_TOKENS
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


async def get_actual_user(request: Request) -> UserInDB:
    """Get actual user from session and validate if is admin or if is disabled

    Args:
        request (Request): Request from FastAPI

    Raises:
        HTTPException: User not Found
        HTTPException: User Disabled
        HTTPException: User is not admin
        HTTPException: Session not valid or not found

    Returns:
        UserInDB: User from database
    """
    user = request.session.get("user")
    if user is not None:
        userDB = UserService.get_user_by_email(user["email"])
        if userDB is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not Found"
            )
        if userDB.disabled == True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User Disabled"
            )
        if userDB.admin == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        return userDB
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )


async def get_api_key(api_key: str = Security(api_key_header)) -> UserInDB:
    """Get api key Bearer from header and validate if is valid and return user

    Args:
        api_key (str, optional): Bearer token from header, Default Authorization header

    Raises:
        HTTPException: Token unvalid
        HTTPException: Token can not be verified

    Returns:
        UserInDB: _description_
    """
    api_key = api_key.replace("Bearer ", "", 1)
    try:
        user = jws.verify(
            api_key, SECRET, algorithms=[configuration.APP_TOKEN_ALGORITHM]
        )
        user_dict = dict(json.loads(user))
        jti = user_dict["jti"]
        ret = TokenService.verify_by_jti(jti)
        user = UserService.get_user_by_username(ret.username)
        if user.admin == False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        actual_user = user
        if ret is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token unvalid"
            )
        else:
            return actual_user
    except JWSError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token can not be verified",
        )


async def get_api_key_public(api_key: str = Security(api_key_header)):
    api_key = api_key.replace("Bearer ", "", 1)
    status_ret, ret = TokenPublicService.validate_token(api_key)
    if status_ret is None and ret is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed Token"
        )
    if status_ret == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
    return ret