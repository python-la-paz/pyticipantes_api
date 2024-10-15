from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import ProgrammingLanguage, ProgrammingLanguageInDB
from app.utils import PyObjectId
from bson import ObjectId

class ProgrammingLanguageService:
    """Service for PROGRAMMING LANGUAGES in database operations"""

    TABLE = db.programming_language  # Asegúrate de que el nombre de la colección sea correcto

    @classmethod
    def get(cls, id: PyObjectId) -> ProgrammingLanguage | None:
        """Get a programming language by id in the database.

        Args:
            id (PyObjectId): ObjectId of the programming language to search in the database.

        Returns:
            ProgrammingLanguage | None: Programming language found or None.
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return ProgrammingLanguage(**search)
        else:
            return None

    @classmethod
    def insert(cls, item: ProgrammingLanguageInDB) -> ProgrammingLanguage | None:
        """Insert a new programming language into the database.

        Args:
            item (ProgrammingLanguageInDB): Programming language to insert into the database.

        Returns:
            ProgrammingLanguage | None: Programming language inserted or None if already exists.
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

        # Comprobar si ya existe un lenguaje de programación con el mismo nombre
        existing_language = cls.get_by_name(item.name)
        if existing_language is None:
            inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
            return cls.get(PyObjectId(inserted.inserted_id))
        else:
            print("Programming language with this name already exists.")
            return None
    
    @classmethod
    def update(cls, item: ProgrammingLanguageInDB) -> ProgrammingLanguage | None:
        """Update a programming language in the database.

        Args:
            item (ProgrammingLanguageInDB): Programming language to update in the database.

        Returns:
            ProgrammingLanguage | None: Updated programming language or None if error.
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
        return ProgrammingLanguage(**ret) if ret else None
    
    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a programming language in the database by id.

        Args:
            id (PyObjectId): ObjectId of the programming language to delete in the database.
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def list(cls) -> List[ProgrammingLanguage]:
        """List all programming languages in the database.

        Returns:
            List of programming languages: List
        """
        finds = cls.TABLE.find({"disabled": False})
        items = [ProgrammingLanguage(**find) for find in finds]
        return items
    
    @classmethod
    def get_by_name(cls, name: str) -> ProgrammingLanguage | None:
        """Retrieve a programming language by name.

        Args:
            name (str): Name of the programming language to find.

        Returns:
            ProgrammingLanguage | None: Programming language found or None if not found.
        """
        language_data = cls.TABLE.find_one({"name": name})
        if language_data:
            return ProgrammingLanguage(**language_data)
        return None

    @classmethod
    def get(cls, programming_language_id: ObjectId) -> ProgrammingLanguage | None:
        """Get a social network by id in the database.

        Args:
            social_network_id (ObjectId): ObjectId of the social network to search in the database.

        Returns:
            SocialNetwork | None: Social network found or None.
        """
        programming_language_data = cls.TABLE.find_one({"_id": programming_language_id})
        if programming_language_data:
            return ProgrammingLanguage(**programming_language_data)
        return None