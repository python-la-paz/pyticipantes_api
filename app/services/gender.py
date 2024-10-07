from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Gender, GenderInDB
from app.utils import PyObjectId


class GenderService:
    """Service for GENDER in database operations"""

    TABLE = db.gender

    @classmethod
    def get(cls, id: PyObjectId) -> Gender | None:
        """Get a gender by id in database

        Args:
            id (PyObjectId): ObjectId of gender to search in database

        Returns:
            Gender | None: Gender found or None
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return Gender(**search)
        else:
            return None

    @classmethod
    def list(cls, page_number: int = 0, n_per_page: int = 100) -> List[Gender]:
        """ List genders in database

        Args:
            page_number (int): Page number to search
            n_per_page (int): Number of items per page

        Returns:
            List of genders: List
        """
        finds = (
            cls.TABLE.find({"disabled": False})
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Gender(**find) for find in finds]
        return items
