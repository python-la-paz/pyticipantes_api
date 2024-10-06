from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Event, EventInDB
from app.utils import PyObjectId


class EventService:
    """Service for EVENTS in database operations"""

    TABLE = db.event

    @classmethod
    def get(cls, id: PyObjectId) -> Event | None:
        """Get a event by id in database

        Args:
            id (PyObjectId): ObjectId of event to search in database

        Returns:
            Event | None: Event found or None
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return Event(**search)
        else:
            return None

    @classmethod
    def insert(cls, item: EventInDB) -> Event | None:
        """Insert a new event in database

        Args:
            item (Event): Event to insert in database

        Returns:
            ObjectId | None: ObjectId of inserted event or None if error
        """
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")
        item.date_insert = datetime.now(timezone.utc)
        inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        ret = cls.get(inserted.inserted_id)
        return ret

    @classmethod
    def update(cls, item: EventInDB) -> Event | None:
        """Update a event in database

        Args:
            item (Event): Event to update in database

        Returns:
            ObjectId | None: ObjectId of updated event or None if error
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
        return Event(**ret)

    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a event in database by id

        Args:
            id (PyObjectId): ObjectId of event to delete in database
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def search(cls, q: str, page_number: int = 0, n_per_page: int = 100) -> List[Event]:
        """Search events by title in database

        Args:
            q (str): Title to search in database
            page_number (int): Page number to search in database
            n_per_page (int): Number of items per page

        Returns:
            List[Event]: List of events found in database
        """
        finds = (
            cls.TABLE.find(
                {
                    "$and": [
                        {"disabled": False},
                        {"title": {"$regex": q, "$options": "i"}},
                    ]
                },
            )
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Event(**find) for find in finds]
        return items

    @classmethod
    def list(cls, page_number: int = 0, n_per_page: int = 100) -> List[Event]:
        finds = (
            cls.TABLE.find({"disabled": False})
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Event(**find) for find in finds]
        return items
