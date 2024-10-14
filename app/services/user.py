from datetime import datetime, timezone

from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models.user import UserInDB
from app.utils import PyObjectId


class UserService:
    """Service for USERS in database operations"""

    TABLE = db.user

    @classmethod
    def insert_or_update_user(cls, user: UserInDB) -> UserInDB | None:
        """Insert or update user in database

        Args:
            user (UserInDB): User to insert or update

        Returns:
            ObjectId | None: ObjectId of inserted or updated user or None if error
        """
        if hasattr(user, "id"):
            delattr(user, "id")
        find = UserService.get_user_by_email(user.email)
        if find is None:
            user.date_insert = datetime.now(timezone.utc)
            user.username = user.email
            ret = cls.TABLE.insert_one(user.model_dump(by_alias=True))
            returned = cls.TABLE.find_one({"_id": ret.inserted_id})
            return UserInDB(**returned)
        else:
            if hasattr(user, "given_name"):
                delattr(user, "given_name")
            if hasattr(user, "family_name"):
                delattr(user, "family_name")
                
            if hasattr(user, "date_insert"):
                delattr(user, "date_insert")
            if hasattr(user, "admin"):
                delattr(user, "admin")
            if hasattr(user, "username"):
                delattr(user, "username")
            # if hasattr(user, "email"):
            #     delattr(user, "email")

            if hasattr(user, "birthday"):
                delattr(user, "birthday")
            if hasattr(user, "gender"):
                delattr(user, "gender")
            if hasattr(user, "dni"):
                delattr(user, "dni")
            if hasattr(user, "profession"):
                delattr(user, "profession")
            if hasattr(user, "place_profession"):
                delattr(user, "place_profession")
            if hasattr(user, "residence"):
                delattr(user, "residence")
            if hasattr(user, "level_programming"):
                delattr(user, "level_programming")
            if hasattr(user, "phone"):
                delattr(user, "phone")

            user.date_update = datetime.now(timezone.utc)
            user.disabled = find.disabled
            ret = cls.TABLE.find_one_and_update(
                {"email": user.email},
                {"$set": user.model_dump(by_alias=True)},
                return_document=ReturnDocument.AFTER,
            )
            return UserInDB(**ret)

    @classmethod
    def get_user_by_email(cls, email: str) -> UserInDB | None:
        """Get user from database by email
        Args:
            email (str): email of user to find

        Returns:
            UserInDB | None: User information if found else None
        """
        ret = cls.TABLE.find_one({"email": email})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None

    @classmethod
    def get_user_by_username(cls, username: str) -> UserInDB | None:
        ret = cls.TABLE.find_one({"username": username, "disabled": False})
        if ret is not None:
            return UserInDB(**ret)
        else:
            return None
        
    @classmethod
    def update_extra_info(cls, user: UserInDB) -> UserInDB | None:
        """Update user extra information in database

        Args:
            user (UserInDB): User to update extra information

        Returns:
            UserInDB | None: User updated or None if error
        """
        if not hasattr(user, "id"):
            return None
        if hasattr(user, "date_insert"):
            delattr(user, "date_insert")
        if hasattr(user, "username"):
            delattr(user, "username")
        if hasattr(user, "email"):
            delattr(user, "email")
        if hasattr(user, "admin"):
            delattr(user, "admin")
        user.date_update = datetime.now(timezone.utc)
        ret = cls.TABLE.find_one_and_update(
            {"_id": user.id},
            {"$set": user.model_dump(by_alias=True)},
            return_document=ReturnDocument.AFTER,
        )
        return UserInDB(**ret)