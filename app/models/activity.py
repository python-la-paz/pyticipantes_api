from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from app.models.additional_info import AdditionalInfoAnswer, AdditionalInfoQuestion

from app.models.fileblob import FileBlob
from app.models.registration import RegistrationPeriod
from app.models.user import User
from app.utils import PyObjectId

class ActivityAPI(RegistrationPeriod):
    event: PyObjectId
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

class Activity(ActivityAPI):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    is_full: Optional[bool] = False

class ActivityInDB(Activity):
    email_enabled: bool = False
    email_template: Optional[str] = None
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None

class ActivityRegister(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    activity: PyObjectId
    user: PyObjectId
    date: datetime
    seat: Optional[int] = 0
    status: Optional[str] = "pending" # pending, accepted, rejected
    note: Optional[str] = None
    document_upload: Optional[FileBlob] = None
    additional_info: Optional[List[AdditionalInfoAnswer]] = Field(default_factory=list)

class ActivityRegisterInDB(ActivityRegister):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None

class ActivityUsersMigration(Activity):
    participants: List[User] = []