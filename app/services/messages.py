from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Messages, MessagesInDB
from app.models.result import StatusCode
from app.utils import PyObjectId

class MessagesService:
    """Service for MESSAGES in database operations"""
    TABLE = db.messages
    @classmethod
    def get_by_code(cls, code: StatusCode) -> Messages:
        """Get a message by code in database """
        search = cls.TABLE.find_one({"code": code.value, "disabled": False})
        if search is not None:
            return Messages(**search)
        else:
            return Messages(code=code, message="Message not found")