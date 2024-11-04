from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public
from app.models import Result, Token, Activity, ActivityRegister
from app.services import ActivityService
from app.services.bl import ActivityRegistration
from app.services.messages import MessagesService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()

@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[Activity]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)

@router.get("", response_model=List[Activity], status_code=status.HTTP_200_OK)
async def get_activities(
    page_number: int = 0,
    n_per_page: int = 100,
):
    """Retrieve a list of activities."""
    search = ActivityRegistration.list_public_activities(
        page_number=page_number, n_per_page=n_per_page
    )
    return search


@router.get("/{id}", response_model=Activity, status_code=status.HTTP_200_OK)
async def get_activity_by_id(
    id: PyObjectId,
):
    """Retrieve an activity by ID."""
    activity = ActivityRegistration.get_public_activity(id=id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post(
    "/{id}/register", response_model=ActivityRegister, status_code=status.HTTP_201_CREATED
)
async def register_in_activity(
    request: Request,
    id: PyObjectId,
    file: Optional[UploadFile] = None,
    additional_info: List[str] = Form([]),
    user: Token = Depends(get_api_key_public),
):
    """Register in an activity."""
    print("ban1")
    try:
        print("ban2")
        size_image = request.headers.get("content-length")
        size_image = int(size_image)
        print("ban4")
    except Exception:
        print("ban3")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Result(message="Invalid image size").model_dump(),
        )
    print("ban5")
    activity_register, error, status_code = ActivityRegistration.register_in_activity(
        id=id,
        username=user.username,
        file=file,
        size_image=size_image,
        additional_info=additional_info,
    )
    print("ban6")
    print(activity_register)
    message = MessagesService.get_by_code(status_code)
    if not activity_register:
        print("ban8")
        print(message.message)
        print(activity_register)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Result(message=message.message, code=message.code).model_dump(),
        )
    print("ban7")
    return activity_register


@router.get(
    "/{id}/register", response_model=List[ActivityRegister], status_code=status.HTTP_200_OK
)
async def get_activity_registers(
    id: PyObjectId,
    user: Token = Depends(get_api_key_public),
):
    """Retrieve all registrations for a specific activity."""
    registers = ActivityRegistration.get_registers(id=id, username=user.username)
    return registers