from typing import List, Optional

import pymongo

from app.core.database import db
from app.models.email_log import EmailLog
from app.utils import PyObjectId


class EmailLogService:
    """Service for registration email attempts stored in database"""

    TABLE = db.email_log

    @classmethod
    def insert(cls, item: EmailLog) -> None:
        cls.TABLE.insert_one(item.model_dump(by_alias=True, exclude={"id"}))

    @classmethod
    def list(
        cls,
        event: Optional[PyObjectId] = None,
        activity: Optional[PyObjectId] = None,
        success: Optional[bool] = None,
        page_number: int = 0,
        n_per_page: int = 100,
    ) -> List[EmailLog]:
        query = {}
        if event is not None:
            query["event"] = event
        if activity is not None:
            query["activity"] = activity
        if success is not None:
            query["success"] = success
        finds = (
            cls.TABLE.find(query)
            .sort("date", pymongo.DESCENDING)
            .skip(((page_number - 1) * n_per_page) if page_number > 0 else 0)
            .limit(n_per_page)
        )
        return [EmailLog(**find) for find in finds]
