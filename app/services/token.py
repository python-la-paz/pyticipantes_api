import hashlib
import uuid
from datetime import datetime, timezone
from jose import jws
from pymongo.collection import ReturnDocument

from app.core import configuration
from app.core.database import db
from app.models.token import Token, TokenUser
from app.utils import current, PyObjectId

SECRET = configuration.APP_SECRET_TOKENS


class TokenService:
    """Service for TOKENS in database operations"""
    TABLE = db.token
    @classmethod
    def create(cls, item: Token) -> TokenUser:
        """Create a new token in database

        Args:
            item (Token): Token to insert in database, required 'username'

        Returns:
            str : Token created (JWS string)
        """
        item.date_insert = datetime.now(timezone.utc)
        item.disabled = False
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")
        unique_id = str(uuid.uuid4())

        payload = {"current": current(), "jti": unique_id}
        token = jws.sign(
            payload, SECRET, algorithm=configuration.APP_TOKEN_ALGORITHM
        )
        item.jti = unique_id
        ret = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        return TokenUser(token=token, jti=unique_id)

    @classmethod
    def get_by_jti_and_username(cls, jti: str, username: str) -> Token | None:
        """
            Get a token by jti and username in database

        Args:
            jti (str): JTI to search in database
            username (str): username to search in database
        
        Returns:
            Token | None: Token found or None
        """
        find = cls.TABLE.find_one(
            {"jti": jti, "username": username, "disabled": False}
        )
        if find is not None:
            return Token(**find)
        else:
            return None
        
    @classmethod
    def verify_by_jti(cls, jti: str) -> Token | None:
        """
            Verify a token by jti in database

        Args:
            jti (str): JTI to search in database
        
        Returns:
            Token | None: Token found or None
        """
        find = cls.TABLE.find_one(
            {"jti": jti, "disabled": False}
        )
        return find

    @classmethod
    def get_token(cls, token: str) -> Token | None:
        """Get a token object by token (JWS string) in database

        Args:
            token (str): Token to search in database (JWS string)

        Returns:
            Token | None: Token found or None
        """
        find = cls.TABLE.find_one({"disabled": False, "token": token})
        return find

    @classmethod
    def get(cls, username: str) -> list[Token]:
        """Get all tokens by username in database

        Args:
            username (str): username to search in database

        Returns:
            list[Token]: List of tokens found
        """
        finds = cls.TABLE.find({"disabled": False, "username": username})
        items = []
        for find in finds:
            items.append(Token(**find))
        return items

    @classmethod
    def search(cls, item: Token) -> list[Token]:
        """Search tokens by username and jti in database

        Args:
            item (Token): Token to search in database, required 'username' and 'jti'

        Returns:
            list[Token]: List of tokens found in database
        """
        finds = cls.TABLE.find(
            {
                "$and": [
                    {"disabled": False},
                    {"username": item.username},
                    {"jti": {"$regex": item.jti}},
                ]
            }
        )
        tokens = []
        for find in finds:
            tokens.append(Token(**find))
        return tokens

    @classmethod
    def delete(cls, item: Token) -> None:
        """Delete a token in database by id and username

        Args:
            item (Token): Token to delete in database, required 'id' and 'username'
        """
        item.date_update = datetime.now(timezone.utc)
        ret = cls.TABLE.find_one_and_update(
            {"_id": item.id, "username": item.username, "disabled": False},
            {
                "$set": {
                    "disabled": True,
                    "date_update": item.date_update,
                    "username_update": item.username_update,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
