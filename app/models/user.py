from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.skills import UserSkill
from app.utils.mongo_validator import PyObjectId


class User(BaseModel):
    """Model for USER, require email and optional username"""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = ""
    email: str
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    disabled: Optional[bool] = False
    admin: Optional[bool] = False
    birthday: Optional[datetime] = None
    gender: Optional[PyObjectId] = None
    dni: Optional[str] = None
    profession: Optional[PyObjectId] = None
    place_profession: Optional[str] = None
    residence: Optional[PyObjectId] = None
    level_programming: Optional[int] = 0
    phone: Optional[str] = None
    programming_languages: List[UserSkill] = []
    new: bool = False


class UserAPI(User):
    """Model for USER in API operations extends from User"""

    data_complete: Optional[bool] = False


class UserInDB(User):
    """Model for USER in database storage extends from User"""

    hashed_password: Optional[str] = None
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
