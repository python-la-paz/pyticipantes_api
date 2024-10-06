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
    TABLE = db.token_public
    @classmethod
    def create(cls, item: Token):
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
        payload = { "exp": expires, "jti": jti}
        token = jwt.encode(payload, SECRET, algorithm=configuration.APP_TOKEN_ALGORITHM)
        item.jti = jti
        item.expires = expires
        ret = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        return ret, token
    
    @classmethod
    def create_mirror(cls, item:Token):
        item.date_insert = datetime.now(timezone.utc)
        item.disabled = False
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")
        expires = datetime.now(timezone.utc) + timedelta(minutes=TIME_EXPIRES)
        item.expires = expires
        ret = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        return ret

    @classmethod
    def delete_by_jti(cls, jti: str):
        ret = db.token_public.find_one_and_update(
            {"jti": jti, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        return ret

    @classmethod
    def validate_token(cls, token: str):
        try:
            payload = jwt.decode(
                token, SECRET, algorithms=[configuration.APP_TOKEN_ALGORITHM]
            )
            ret = TokenPublicService.get_by_jti(payload.get("jti"))
            if ret is None:
                return False, None
            username = ret.username
            activeUser = UserService.get_user_by_username(username)
            if activeUser is None:
                TokenPublicService.delete_by_jti(payload.get("jti"))
                return False, None
            return True, Token(username=username, jti=payload.get("jti"), token="")
        except JWTError:
            return None, None

    @classmethod
    def get_by_jti(cls, jti: str) -> Token | None:
        ret = cls.TABLE.find_one({"jti": jti, "disabled": False})
        if ret is not None:
            return Token(**ret)
        return None
