from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.activity import Activity, ActivityRegister, ActivityUsersMigration
from app.models.additional_info import AdditionalInfoAnswer, AdditionalInfoQuestion
from app.models.fileblob import FileBlob
from app.models.registration import REGISTRATION_TIMEZONE, RegistrationPeriod
from app.models.user import User
from app.utils import PyObjectId


class EventAPI(RegistrationPeriod):
    title: str
    description: str
    date: datetime
    location: str
    location_map: Optional[str] = None
    image: Optional[FileBlob] = None
    document: Optional[str] = None
    document_type: Optional[str] = None
    link: Optional[str] = None
    link_text: Optional[str] = None
    public: Optional[bool] = False
    quota: Optional[int] = 0
    price: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    finished: Optional[bool] = False
    tags: Optional[List[str]] = []
    organizers: Optional[List[str]] = []
    additional_info: Optional[List[AdditionalInfoQuestion]] = Field(default_factory=list)
    document_required: Optional[bool] = False
    automatic: Optional[bool] = False

class Event(EventAPI):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class EventInDB(Event):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None

class EventRegister(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    event: PyObjectId
    user: PyObjectId
    date: datetime
    seat: Optional[int] = 0
    status: Optional[str] = "pending" # pending, accepted, rejected
    note: Optional[str] = None
    document_upload: Optional[FileBlob] = None
    additional_info: Optional[List[AdditionalInfoAnswer]] = Field(default_factory=list)
    rrss: Optional[PyObjectId] = None

class EventRegisterInDB(EventRegister):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None

class EventRegisterMigration(Event):
    participants: List[User] = []
    activities: List[ActivityUsersMigration] = []