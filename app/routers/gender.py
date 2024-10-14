from typing import List, Optional
from fastapi import APIRouter, Depends, status

from app.auth.access import get_actual_user
from app.models import Gender, UserInDB, GenderInDB
from app.models.gender import Gender
from app.services import GenderService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()


@router.get("", response_model=List[Gender], status_code=status.HTTP_200_OK)
async def get_genders(user: UserInDB = Depends(get_actual_user)):
    """Retrieve a list of genders."""
    return GenderService.list()


@router.get("/{id}", response_model=Gender, status_code=status.HTTP_200_OK)
async def get_gender_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Retrieve a gender by ID."""
    return GenderService.get(id=id)


@router.post("", response_model=Gender, status_code=status.HTTP_201_CREATED)
async def create_gender(gender: Gender, user: UserInDB = Depends(get_actual_user)):
    """Create a new gender."""
    genderdb = GenderInDB(**gender.model_dump(by_alias=True))
    genderdb.username_insert = user.username
    return GenderService.insert(item=genderdb)


@router.put("/{id}", response_model=Gender, status_code=status.HTTP_200_OK)
async def update_gender(
    id: PyObjectId, gender: Gender, user: UserInDB = Depends(get_actual_user)
):
    """Update an existing gender."""
    genderdb = GenderInDB(**gender.model_dump(by_alias=True))
    genderdb.id = id
    genderdb.username_update = user.username
    return GenderService.update(item=genderdb)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gender(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Delete a gender by ID."""
    GenderService.delete(id=id)
    return None