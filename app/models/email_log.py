from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.utils import PyObjectId


class EmailLog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    date: datetime
    email: str
    user: Optional[PyObjectId] = None
    username: str = ""
    item_type: Literal["event", "activity"]
    event: Optional[PyObjectId] = None
    activity: Optional[PyObjectId] = None
    registration: Optional[PyObjectId] = None
    subject: Optional[str] = None
    template: Optional[str] = None
    success: bool
    error: Optional[str] = None
