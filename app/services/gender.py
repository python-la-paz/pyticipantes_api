from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import Gender, GenderInDB
from app.utils import PyObjectId
from bson import ObjectId


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
    def insert(cls, item: GenderInDB) -> Gender | None:
        """Insert a new gender in the database.

        Args:
            item (GenderInDB): Gender to insert in database.

        Returns:
            Gender | None: Gender inserted or None if already exists.
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
        existing_gender = cls.get_by_name(item.name)  # Asegúrate de tener un método para buscar por nombre
        if existing_gender is None:
            inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
            return cls.get(PyObjectId(inserted.inserted_id))
        else:
            print("Gender with this name already exists.")
            return None
    
    @classmethod
    def update(cls, item: GenderInDB) -> Gender | None:
        """Update a gender in database

        Args:
            item (GenderInDB): Gender to update in database

        Returns:
            Gender | None: Updated gender or None if error
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
        return Gender(**ret) if ret else None
    
    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a gender in database by id

        Args:
            id (PyObjectId): ObjectId of gender to delete in database
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def list(cls) -> List[Gender]:
        """List all genders in the database.

        Returns:
            List of genders: List
        """
        finds = cls.TABLE.find({"disabled": False})
        items = [Gender(**find) for find in finds]
        return items
    
    @classmethod
    def get_by_name(cls, name: str) -> Gender | None:
        """Retrieve a gender by name.

        Args:
            name (str): Name of the gender to find.

        Returns:
            Gender | None: Gender found or None if not found.
        """
        gender_data = cls.TABLE.find_one({"name": name})
        if gender_data:
            return Gender(**gender_data)  # Asegúrate de tener un modelo para esto
        return None

    @classmethod
    def get(cls, gender_id: ObjectId) -> Gender | None:
        """Retrieve a gender by ID.

        Args:
            gender_id (ObjectId): ID of the gender to find.

        Returns:
            Gender | None: Gender found or None if not found.
        """
        gender_data = cls.TABLE.find_one({"_id": gender_id})
        if gender_data:
            return Gender(**gender_data)  # Asegúrate de tener un modelo para esto
        return None