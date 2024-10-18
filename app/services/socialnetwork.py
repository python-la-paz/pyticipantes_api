from datetime import datetime, timezone
from typing import List
from pymongo.collection import ReturnDocument

from app.core.database import db
from app.models import SocialNetwork, SocialNetworkInDB
from app.utils import PyObjectId
from bson import ObjectId


class SocialNetworkService:
    """Service for SOCIAL NETWORK in database operations"""

    TABLE = db.social_network

    @classmethod
    def get(cls, id: PyObjectId) -> SocialNetwork | None:
        """Get a social network by id in the database.

        Args:
            id (PyObjectId): ObjectId of the social network to search in the database.

        Returns:
            SocialNetwork | None: Social network found or None.
        """
        search = cls.TABLE.find_one({"_id": id, "disabled": False})
        if search is not None:
            return SocialNetwork(**search)
        else:
            return None

    @classmethod
    def insert(cls, item: SocialNetworkInDB) -> SocialNetwork | None:
        """Insert a new social network into the database.

        Args:
            item (SocialNetworkInDB): Social network to insert into the database.

        Returns:
            SocialNetwork | None: Social network inserted or None if already exists.
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

        # Comprobar si ya existe una red social con el mismo nombre
        existing_social_network = cls.get_by_name(item.name)
        if existing_social_network is None:
            inserted = cls.TABLE.insert_one(item.model_dump(by_alias=True))
            return cls.get(PyObjectId(inserted.inserted_id))
        else:
            print("Social network with this name already exists.")
            return None
    
    @classmethod
    def update(cls, item: SocialNetworkInDB) -> SocialNetwork | None:
        """Update a social network in the database.

        Args:
            item (SocialNetworkInDB): Social network to update in the database.

        Returns:
            SocialNetwork | None: Updated social network or None if error.
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
        return SocialNetwork(**ret) if ret else None
    
    @classmethod
    def delete(cls, id: PyObjectId) -> None:
        """Delete a social network in the database by id.

        Args:
            id (PyObjectId): ObjectId of the social network to delete in the database.
        """
        cls.TABLE.find_one_and_update(
            {"_id": id, "disabled": False},
            {"$set": {"disabled": True, "date_update": datetime.now(timezone.utc)}},
        )

    @classmethod
    def list(cls) -> List[SocialNetwork]:
        """List all social networks in the database.

        Returns:
            List of social networks: List
        """
        finds = cls.TABLE.find({"disabled": False})
        items = [SocialNetwork(**find) for find in finds]
        return items
    
    @classmethod
    def get_by_name(cls, name: str) -> SocialNetwork | None:
        """Retrieve a social network by name.

        Args:
            name (str): Name of the social network to find.

        Returns:
            SocialNetwork | None: Social network found or None if not found.
        """
        social_network_data = cls.TABLE.find_one({"name": name})
        if social_network_data:
            return SocialNetwork(**social_network_data)
        return None

    @classmethod
    def get(cls, social_network_id: ObjectId) -> SocialNetwork | None:
        """Get a social network by id in the database.

        Args:
            social_network_id (ObjectId): ObjectId of the social network to search in the database.

        Returns:
            SocialNetwork | None: Social network found or None.
        """
        social_network_data = cls.TABLE.find_one({"_id": social_network_id})
        if social_network_data:
            return SocialNetwork(**social_network_data)
        return None