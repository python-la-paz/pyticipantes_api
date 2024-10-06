import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pymongo.collection import ReturnDocument

from app.core import configuration
from app.core.database import db
from app.models import Token
from app.services import UserService

SECRET = configuration.APP_SECRET_TOKENS
TIME_EXPIRES = configuration.APP_TOKEN_EXPIRES


class TokenPublicService:
    @staticmethod
    def create(item: Token):
        item.date_insert = datetime.now(timezone.utc)
        item.disabled = False
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")
        jti = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(minutes=TIME_EXPIRES)
        payload = {"sub": item.username, "exp": expires, "jti": jti}
        token = jwt.encode(payload, SECRET, algorithm=configuration.APP_TOKEN_ALGORITHM)
        item.jti = jti
        item.expires = expires
        ret = db.token_public.insert_one(item.model_dump(by_alias=True))
        return ret, token

    @staticmethod
    def delete_by_jti(jti: str):
        ret = db.token_public.find_one_and_update(
            {"jti": jti, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return ret

    @staticmethod
    def validate_token(token: str):
        try:
            payload = jwt.decode(
                token, SECRET, algorithms=[configuration.APP_TOKEN_ALGORITHM]
            )
            ret = TokenPublicService.get_by_jti(payload.get("jti"))
            if ret is None:
                return False, None
            username = username = payload.get("sub")
            activeUser = UserService.get_user_public(username)
            if activeUser is None:
                TokenPublicService.delete_by_jti(payload.get("jti"))
                return False, None
            return True, Token(username=username, jti=payload.get("jti"), token="")
        except JWTError:
            return None, None

    @staticmethod
    def get_by_jti(jti: str):
        ret = db.token_public.find_one({"jti": jti, "disabled": False})
        return ret
