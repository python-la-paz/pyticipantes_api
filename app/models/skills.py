from pydantic import BaseModel

from app.utils.mongo_validator import PyObjectId


class UserSkill(BaseModel):
    """Model for USER SKILL, require skill and level"""

    skill: PyObjectId
    name: str
    level: int
