from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.utils import PyObjectId


class EventAPI(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    location_map: Optional[str] = None
    image: Optional[str] = None
    document: Optional[str] = None
    link: Optional[str] = None
    public: Optional[bool] = False
    quota: Optional[int] = 0
    price: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    tags: Optional[List[str]] = []

class Event(EventAPI):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class EventInDB(Event):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None