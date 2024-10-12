from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.utils import PyObjectId

class Profession(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str


class ProfessionInDB(Profession):
    disabled: Optional[bool] = False
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
    username_insert: Optional[str] = None
    username_update: Optional[str] = None
