from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, status

from app.auth.access import get_actual_user, get_api_key
from app.models import Event, EventInDB, FileBlob, UserInDB
from app.models.activity import ActivityUsersMigration
from app.models.event import EventAPI, EventRegisterMigration
from app.models.user import User
from app.services import EventService
from app.services.activity import ActivityService
from app.services.bl.event_register import EventRegistration
from app.services.user import UserService
from app.utils import google_cloud_storage
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.get("", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_event(
    user: UserInDB = Depends(get_actual_user),
    q: Optional[str] = None,
    page_number: int = 0,
    n_per_page: int = 100,
):
    if q is not None:
        search = EventService.search(
            q=q, page_number=page_number, n_per_page=n_per_page
        )
    else:
        search = EventService.list(page_number=page_number, n_per_page=n_per_page)
    return search


@router.get("/{id}", response_model=Event, status_code=status.HTTP_200_OK)
async def get_event_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    return EventService.get(id=id)


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventAPI, user: UserInDB = Depends(get_actual_user)):
    eventdb = EventInDB(**event.model_dump(by_alias=True))
    eventdb.username_insert = user.username
    return EventService.insert(item=eventdb)


@router.put("/{id}", response_model=Event, status_code=status.HTTP_200_OK)
async def update_event(
    id: PyObjectId, event: EventAPI, user: UserInDB = Depends(get_actual_user)
):
    eventdb = EventInDB(**event.model_dump(by_alias=True))
    eventdb.id = id
    eventdb.username_update = user.username
    return EventService.update(item=eventdb)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    EventService.delete(id=id)
    return None


@router.post("/{id}/image", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    id: PyObjectId, image: UploadFile, user: UserInDB = Depends(get_actual_user)
):
    eventdb = EventService.get(id=id)
    if eventdb is None:
        raise Exception("Event not found")
    result, filename, url, content_type = google_cloud_storage.upload_file(
        f"Event:{eventdb.id}",
        image.filename,
        image.content_type,
        image.file,
        public=True,
    )
    if result:
        blob = FileBlob(name=filename, url=url, content_type=content_type)
        eventdb.image = blob
    else:
        raise Exception("Error uploading image")
    eventdb = EventInDB(**eventdb.model_dump(by_alias=True))
    eventdb.username_update = user.username
    return EventService.update(item=eventdb)


@router.post(
    "/{id}/users",
    response_model=EventRegisterMigration,
)
async def get_users_by_event(id: PyObjectId, migrated_ids: List[PyObjectId] = [], user: UserInDB = Depends(get_api_key)):
    eventdb = EventService.get(id=id)
    if eventdb is None:
        raise Exception("Event not found")
    event_registers = EventService.get_all_registers(id=id)
    users = UserService.get_users_by_ids(ids=[er.user for er in event_registers], not_ids=migrated_ids)

    eventRegisterMigration = EventRegisterMigration(**eventdb.model_dump(by_alias=True))
    eventRegisterMigration.participants = users

    activities = ActivityService.get_activities_by_event(id)
    activityUsersMigration = [
        ActivityUsersMigration(**activity.model_dump(by_alias=True))
        for activity in activities
    ]
    eventRegisterMigration.activities = activityUsersMigration
    for activity in activityUsersMigration:
        activity_registers = ActivityService.get_all_registers(id=activity.id)
        users = UserService.get_users_by_ids(ids=[er.user for er in activity_registers], not_ids=migrated_ids)
        activity.participants = users

    return eventRegisterMigration

@router.post(
    "/{id}/users/{dni}",
    response_model=User,
)
async def get_user_by_event(id: PyObjectId, dni: str, user: UserInDB = Depends(get_api_key)):
    eventdb = EventService.get(id=id)
    if eventdb is None:
        raise Exception("Event not found")
    user, more_than_one  = UserService.get_user_by_ci(dni=dni)
    if more_than_one:
        raise Exception("More than one user found")
    if user is None:
        raise Exception("User not found")
    register = EventService.get_register_by_user(id=id, user=user.id)
    if register is None:
        return None
    return user