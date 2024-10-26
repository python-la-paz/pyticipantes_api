from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.access import get_actual_user
from app.models import Activity, UserInDB, ActivityInDB
from app.services import ActivityService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.get("", response_model=List[Activity], status_code=status.HTTP_200_OK)
async def get_activities(user: UserInDB = Depends(get_actual_user)):
    """Retrieve a list of activities."""
    return ActivityService.list()


@router.get("/{id}", response_model=Activity, status_code=status.HTTP_200_OK)
async def get_activity_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Retrieve an activity by ID."""
    activity = ActivityService.get(id=id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(activity: Activity, user: UserInDB = Depends(get_actual_user)):
    """Create a new activity."""
    activity_db = ActivityInDB(**activity.model_dump(by_alias=True))
    activity_db.username_insert = user.username
    return ActivityService.insert(item=activity_db)


@router.put("/{id}", response_model=Activity, status_code=status.HTTP_200_OK)
async def update_activity(
    id: PyObjectId, activity: Activity, user: UserInDB = Depends(get_actual_user)
):
    """Update an existing activity."""
    activity_db = ActivityInDB(**activity.model_dump(by_alias=True))
    activity_db.id = id
    activity_db.username_update = user.username
    return ActivityService.update(item=activity_db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Delete an activity by ID."""
    ActivityService.delete(id=id)
    return None
