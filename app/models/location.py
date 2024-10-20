from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils import PyObjectId


class Location(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str


class LocationInDB(Location):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
