from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Activity, ActivityInDB
from app.utils import PyObjectId
from bson import ObjectId


class ActivityService:
    """Service for ACTIVITY in database operations"""

    TABLE = db.activity  # Asegúrate de que el nombre de la colección sea correcto

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
    
    

    
