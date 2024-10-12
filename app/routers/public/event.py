from typing import List, Optional

from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public
from app.core.configuration import MAX_SIZE_IMAGE_MB
from app.models import Event, EventRegister, Result, Token
from app.services.bl import EventRegistration, UserProfileService
from app.utils.content_types import CONTENT_TYPES_IMAGE, CONTENT_TYPES_VALID
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[Event]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
@router.get("", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_events(
    page_number: int = 0,
    n_per_page: int = 100,
):
    search = EventRegistration.list_public_events(
        page_number=page_number, n_per_page=n_per_page
    )
    return search


@router.get("/{id}", response_model=Event, status_code=status.HTTP_200_OK)
async def get_event_by_id(
    id: PyObjectId,
):
    event = EventRegistration.get_public_event(id=id)
    return event


@router.post(
    "/{id}/register", response_model=EventRegister, status_code=status.HTTP_201_CREATED
)
async def register_in_event(
    request: Request,
    id: PyObjectId,
    file: UploadFile,
    additional_info: List[str] = [],
    user: Token = Depends(get_api_key_public),
):
    try:
        size_image = request.headers.get("content-length")
        size_image = int(size_image)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Result(message="Tamaño de imagen no válido").model_dump(),
        )
    event_register, error = EventRegistration.register_in_event(
        id=id,
        username=user.username,
        file=file,
        size_image=size_image,
        additional_info=additional_info,
    )
    if not event_register:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Result(message=error).model_dump(),
        )
    return event_register


@router.get(
    "/{id}/register", response_model=List[EventRegister], status_code=status.HTTP_200_OK
)
async def get_event_registers(
    id: PyObjectId,
    user: Token = Depends(get_api_key_public),
):
    registers = EventRegistration.get_registers(id=id, username=user.username)
    return registers
