from datetime import datetime, timezone
from typing import List
import pymongo
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Activity, ActivityInDB, ActivityRegister, ActivityRegisterInDB
from app.utils import PyObjectId




class ActivityService:
    """Service for ACTIVITY in database operations"""

    TABLE = db.activity
    TABLE_REGISTER = db.activity_register

    @classmethod
    def get(cls, id: PyObjectId) -> Activity | None:
        """Get an activity by id in the database.

        Args:
            id (PyObjectId): ObjectId of the activity to search in the database.

        Returns:
            Activity | None: Activity found or None.
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return Activity(**search)
        else:
            return None

    @classmethod
    def insert(cls, item: ActivityInDB) -> Activity | None:
        """Insert a new activity into the database.

        Args:
            item (ActivityInDB): Activity to insert into the database.

        Returns:
            Activity | None: Activity inserted or None if already exists.
        """
        item.date_insert = datetime.now(timezone.utc)
        item.disabled = False

        # Limpiar atributos innecesarios
        if hasattr(item, "date_update"):
            delattr(item, "date_update")
        if hasattr(item, "id"):
            delattr(item, "id")
        if hasattr(item, "username_update"):
            delattr(item, "username_update")

        # Insertar la actividad sin comprobación de nombre
        inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
        return cls.get(PyObjectId(inserted.inserted_id))
    
    @classmethod
    def update(cls, item: ActivityInDB) -> Activity | None:
        """Update an activity in the database.

        Args:
            item (ActivityInDB): Activity to update in the database.

        Returns:
            Activity | None: Updated activity or None if error.
        """
        if not hasattr(item, "id"):
            return None
        if hasattr(item, "date_insert"):
            delattr(item, "date_insert")
        if hasattr(item, "username_insert"):
            delattr(item, "username_insert")

        item.date_update = datetime.now(timezone.utc)
        ret = cls.TABLE.find_one_and_update(
            {"_id": item.id, "disabled": False},
            {"$set": item.model_dump(by_alias=True)},
            return_document=ReturnDocument.AFTER,
        )
        return Activity(**ret) if ret else None
    
    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete an activity in the database by id.

        Args:
            id (PyObjectId): ObjectId of the activity to delete in the database.
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def list(cls) -> List[Activity]:
        """List all activities in the database.

        Returns:
            List of activities: List
        """
        finds = cls.TABLE.find({"disabled": False})
        items = [Activity(**find) for find in finds]
        return items
    

    @classmethod
    def search(cls, q: str, page_number: int = 0, n_per_page: int = 100) -> List[Activity]:
        """Search activities by title in database.

        Args:
            q (str): Title to search in database.
            page_number (int): Page number to search in database.
            n_per_page (int): Number of items per page.

        Returns:
            List[Activity]: List of activities found in database.
        """
        finds = (
            cls.TABLE.find(
                {
                    "$and": [
                        {"disabled": False},
                        {"title": {"$regex": q, "$options": "i"}},
                    ]
                }
            )
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Activity(**find) for find in finds]
        return items
    
    @classmethod
    def list_public_activities(cls, page_number: int = 0, n_per_page: int = 100) -> List[Activity]:
        finds = (
            cls.TABLE.find({"disabled": False, "public": True})
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        items = [Activity(**find) for find in finds]
        return items

    @classmethod
    def get_public_activity(cls, id: PyObjectId) -> Activity:
        find = cls.TABLE.find_one({"_id": id, "disabled": False, "public": True})
        return Activity(**find)

    @classmethod
    def get_public_not_finished(cls, id: PyObjectId) -> Activity | None:
        search = cls.TABLE.find_one(
            {"_id": id, "disabled": False, "public": True, "finished": False}
        )
        if search is not None:
            return Activity(**search)
        else:
            return None

    @classmethod
    def is_full(cls, activity: Activity) -> bool:
        if not activity.quota:
            return False, 0
        count = cls.TABLE_REGISTER.count_documents(
            {
                "activity": activity.id,
                "disabled": False,
                "status": {"$in": ["pending", "accepted"]},
            }
        )
        if count >= activity.quota:
            return True, count
        return False, count

    @classmethod
    def is_already_registered(cls, activity: Activity, user: PyObjectId) -> bool:
        count = cls.TABLE_REGISTER.count_documents(
            {
                "activity": activity.id,
                "user": user,
                "disabled": False,
                "status": {"$in": ["pending", "accepted"]},
            }
        )
        return count > 0

    @classmethod
    def get_register(cls, id: PyObjectId) -> ActivityRegister | None:
        """Get an activity register by id in the database.

        Args:
            id (PyObjectId): ObjectId of the activity register to search in the database.

        Returns:
            ActivityRegister | None: Activity register found or None.
        """
        search = cls.TABLE_REGISTER.find_one({"_id": id, "disabled": False})
        if search is not None:
            return ActivityRegister(**search)
        else:
            return None

    @classmethod
    def register_in_activity(cls, activity: ActivityRegisterInDB) -> Activity | None:
        if hasattr(activity, "id"):
            delattr(activity, "id")
        if hasattr(activity, "date_update"):
            delattr(activity, "date_update")
        if hasattr(activity, "username_update"):
            delattr(activity, "username_update")
        activity.date_insert = datetime.now(timezone.utc)
        inserted = cls.TABLE_REGISTER.insert_one(activity.model_dump(by_alias=True))
        ret = cls.get_register(inserted.inserted_id)
        return ret

    @classmethod
    def get_registers(cls, id: PyObjectId, user: PyObjectId) -> List[ActivityRegister]:
        finds = cls.TABLE_REGISTER.find(
            {"disabled": False, "activity": id, "user": user}
        ).sort("date", pymongo.DESCENDING)
        items = [ActivityRegister(**find) for find in finds]
        return items    
