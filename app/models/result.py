from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.mongo_validator import PyObjectId

class StatusCode(str, Enum):
    DEFAULT = "default"
    REGISTER_COMPLETE = "register_complete"
    USER_NOT_FOUND = "user_not_found"
    USER_DATA_NOT_COMPLETE = "user_data_not_complete"
    EVENT_NOT_FOUND = "event_not_found"
    EVENT_ALREADY_FINISHED = "event_already_finished"
    EVENT_FULL = "event_full"
    USER_ALREADY_REGISTERED = "user_already_registered"
    NO_VALID_CONTENT_TYPE = "no_valid_content_type"
    MAX_SIZE_ENABLED = "max_size_enabled"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    RESPONSES_NOT_COMPLETE = "responses_not_complete"
    ERROR_REGISTERING = "error_registering"
    RRSS_REQUIRED = "rrss_required"
    RRSS_NOT_FOUND = "rrss_not_found"
    ACTIVITY_NOT_FOUND = "activity_not_found"
    ACTIVITY_ALREADY_FINISHED = "activity_already_finished"
    ACTIVITY_FULL = "activity_full"
    REGISTER_NOT_FOUND = "register_not_found"


class Result(BaseModel):
    """Model for Result, used in API operations, require message"""
    message: str = "Status"
    code: StatusCode = StatusCode.DEFAULT

    class Config:
        use_enum_values = True  # Esto serializa el valor del Enum automáticamente

class Messages(BaseModel):
    """Model for messages, used in API operations, require message"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    code: StatusCode = StatusCode.DEFAULT
    message: str = "Status"

class MessagesInDB(Messages):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None