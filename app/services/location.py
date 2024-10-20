from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Location, LocationInDB
from app.utils import PyObjectId
from bson import ObjectId

class LocationService:
    """Service for LOCATION in database operations"""

    TABLE = db.location

    @classmethod
    def get(cls, id: PyObjectId) -> Location | None:
        """Get a location by id in database

        Args:
            id (PyObjectId): ObjectId of location to search in database

        Returns:
            Location | None: Location found or None
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return Location(**search)
        else:
            return None

    @classmethod
    def insert(cls, item: LocationInDB) -> Location | None:
        """Insert a new location in the database.

        Args:
            item (LocationInDB): Location to insert in database.

        Returns:
            Location | None: Location inserted or None if already exists.
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

        # Comprobar si ya existe un género con el mismo nombre
        existing_location = cls.get_by_name(item.name)  # Asegúrate de tener un método para buscar por nombre
        if existing_location is None:
            inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
            return cls.get(PyObjectId(inserted.inserted_id))
        else:
            print("Location with this name already exists.")
            return None
    
    @classmethod
    def update(cls, item: LocationInDB) -> Location | None:
        """Update a location in database

        Args:
            item (LocationInDB): Location to update in database

        Returns:
            Location | None: Updated location or None if error
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
        return Location(**ret) if ret else None
    
    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a location in database by id

        Args:
            id (PyObjectId): ObjectId of location to delete in database
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def list(cls) -> List[Location]:
        """List all locations in the database.

        Returns:
            List of locations: List
        """
        finds = cls.TABLE.find({"disabled": False})
        items = [Location(**find) for find in finds]
        return items
    
    @classmethod
    def get_by_name(cls, name: str) -> Location | None:
        """Retrieve a location by name.

        Args:
            name (str): Name of the location to find.

        Returns:
            Location | None: Location found or None if not found.
        """
        location_data = cls.TABLE.find_one({"name": name})
        if location_data:
            return Location(**location_data)  # Asegúrate de tener un modelo para esto
        return None
    
    @classmethod
    def get(cls, location_id: ObjectId) -> Location | None:
        """Retrieve a location by ID.

        Args:
            location_id (ObjectId): ID of the location to find.

        Returns:
            Location | None: Location found or None if not found.
        """
        location_data = cls.TABLE.find_one({"_id": location_id})
        if location_data:
            return Location(**location_data)  # Asegúrate de tener un modelo para esto
        return None
