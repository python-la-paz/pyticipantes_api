from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Profession, ProfessionInDB
from app.utils import PyObjectId


class ProfessionService:
    """Service for PROFESSION in database operations"""

    TABLE = db.profession

    @classmethod
    def get(cls, id: PyObjectId) -> Profession | None:
        """Get a profession by id in database

        Args:
            id (PyObjectId): ObjectId of profession to search in database

        Returns:
            Profession | None: Profession found or None
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return Profession(**search)
        else:
            return None

    @classmethod
    def list(cls, page_number: int = 0, n_per_page: int = 100) -> List[Profession]:
        """ List professions in database

        Args:
            page_number (int): Page number to search
            n_per_page (int): Number of items per page

        Returns:
            List of professions: List
        """
        finds = (
            cls.TABLE.find({"disabled": False})
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Profession(**find) for find in finds]
        return items
    
    @classmethod
    def insert(cls, item: ProfessionInDB) -> Profession | None:
        """Insert a new profession in database

        Args:
            item (Profession): Profession to insert in database

        Returns:
            ObjectId | None: ObjectId of inserted event or None if error
        """
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")
        item.date_insert = datetime.now(timezone.utc)
        inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        ret = cls.get(inserted.inserted_id)
        return ret
    
    @classmethod
    def update(cls, item: ProfessionInDB) -> Profession | None:
        """Update a profession in database

        Args:
            item (Profession): Profession to update in database

        Returns:
            ObjectId | None: ObjectId of updated profession or None if error
        """
        if not hasattr(item, "id"):
            return None
        if hasattr(item, "date_insert"):
            delattr(item, "date_insert")
        if hasattr(item, "username_insert"):
            delattr(item, "username_insert")
        item.date_update = datetime.now(timezone.utc)
        ret = cls.TABLE.find_one_and_update(
            {"_id": item.id},
            {"$set": item.model_dump(by_alias=True)},
            return_document=ReturnDocument.AFTER,
        )
        return Profession(**ret)

    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a profession in database by id

        Args:
            id (PyObjectId): ObjectId of profession to delete in database
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )