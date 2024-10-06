from typing import List, Optional
from fastapi import APIRouter, Depends, status

from app.auth.access import get_actual_user
from app.models import Event, UserInDB, EventInDB
from app.services import EventService
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
async def create_event(event: Event, user: UserInDB = Depends(get_actual_user)):
    eventdb = EventInDB(**event.model_dump(by_alias=True))
    eventdb.username_insert = user.username
    return EventService.insert(item=eventdb)
