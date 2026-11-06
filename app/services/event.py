from datetime import datetime, timezone
from typing import List

import pymongo
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Event, EventInDB, EventRegister, EventRegisterInDB
from app.utils import PyObjectId


class EventService:
    """Service for EVENTS in database operations"""

    TABLE = db.event
    TABLE_REGISTER = db.event_register

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

    @classmethod
    def list_public_events(
        cls, page_number: int = 0, n_per_page: int = 100, order: str = "-id"
    ) -> List[Event]:
        order_field = order.lstrip("-")
        if order_field == "id":
            order_field = "_id"
        order_direction = (
            pymongo.DESCENDING if order.startswith("-") else pymongo.ASCENDING
        )
        finds = (
            cls.TABLE.find({"disabled": False, "public": True})
            .sort(order_field, order_direction)
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Event(**find) for find in finds]
        return items

    @classmethod
    def get_public_event(cls, id: PyObjectId) -> Event:
        find = cls.TABLE.find_one({"_id": id, "disabled": False, "public": True})
        return Event(**find)

    @classmethod
    def get_public_no_finished(cls, id: PyObjectId) -> Event | None:
        search = cls.TABLE.find_one(
            {"_id": id, "disabled": False, "public": True, "finished": False}
        )
        if search is not None:
            return Event(**search)
        else:
            return None

    @classmethod
    def is_full(cls, event: Event) -> bool:
        count = cls.TABLE_REGISTER.count_documents(
            {
                "event": event.id,
                "disabled": False,
                "status": {"$in": ["pending", "accepted"]},
            }
        )
        if not event.quota:
            return False, count
        if count >= event.quota:
            return True, count
        return False, count

    @classmethod
    def is_already_registered(cls, event: Event, user: PyObjectId) -> bool:
        count = cls.TABLE_REGISTER.count_documents(
            {
                "event": event.id,
                "user": user,
                "disabled": False,
                "status": {"$in": ["pending", "accepted"]},
            }
        )
        return count > 0

    @classmethod
    def get_register(cls, id: PyObjectId) -> EventRegister | None:
        """Get a event register by id in database

        Args:
            id (PyObjectId): ObjectId of event register to search in database

        Returns:
            EventRegister | None: Event register found or None
        """
        search = cls.TABLE_REGISTER.find_one({"_id": id, "disabled": False})
        if search is not None:
            return EventRegister(**search)
        else:
            return None

    @classmethod
    def register_in_event(cls, event: EventRegisterInDB) -> Event | None:
        if hasattr(event, "id"):
            delattr(event, "id")
        if hasattr(event, "date_update"):
            delattr(event, "date_update")
        if hasattr(event, "username_update"):
            delattr(event, "username_update")
        event.date_insert = datetime.now(timezone.utc)
        inserted = cls.TABLE_REGISTER.insert_one(event.model_dump(by_alias=True))
        ret = cls.get_register(inserted.inserted_id)
        return ret

    @classmethod
    def get_registers(cls, id: PyObjectId, user: PyObjectId) -> List[EventRegister]:
        finds = cls.TABLE_REGISTER.find(
            {"disabled": False, "event": id, "user": user}
        ).sort("date", pymongo.DESCENDING)
        items = [EventRegister(**find) for find in finds]
        return items

    @classmethod
    def get_all_registers(cls, id: PyObjectId) -> List[EventRegister]:
        finds = cls.TABLE_REGISTER.find(
            {"disabled": False, "event": id, "status": {"$in": ["accepted"]}}
        ).sort("date", pymongo.DESCENDING)
        items = [EventRegister(**find) for find in finds]
        return items


    @classmethod
    def get_register_by_user(cls, id: PyObjectId, user: PyObjectId) -> EventRegister | None:
        search = cls.TABLE_REGISTER.find_one(
            {"event": id, "user": user, "disabled": False, "status": {"$in": ["pending", "accepted"]}}
        )
        if search is not None:
            return EventRegister(**search)
        else:
            return None