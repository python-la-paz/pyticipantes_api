from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public, get_actual_user
from app.models import Profession, ProfessionInDB, Result, Token, UserAPI, UserInDB
from app.services import ProfessionService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()

@router.get("", response_model=List[Profession], status_code=status.HTTP_200_OK)
async def get_professions(user: UserInDB = Depends(get_actual_user)):
    """Retrieve a list of professions."""
    return ProfessionService.list()

@router.get("/{id}", response_model=Profession, status_code=status.HTTP_200_OK)
async def get_profession_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Retrieve a profession by ID"""
    return ProfessionService.get(id=id)

@router.post("", response_model=Profession, status_code=status.HTTP_200_OK)
async def create_profession(profession:Profession, user: UserInDB = Depends(get_actual_user)):
    """Create a new profession"""
    professiondb =  ProfessionInDB(**profession.model_dump(by_alias=True))
    professiondb.username_insert = user.username
    return ProfessionService.insert(item=professiondb)

@router.put("/{id}", response_model=Profession, status_code=status.HTTP_200_OK)
async def update_profession(
    id: PyObjectId, profession:Profession, user: UserInDB = Depends(get_actual_user)
    ):
    """Update a profession by ID"""
    professiondb =  ProfessionInDB(**profession.model_dump(by_alias=True))
    professiondb.id = id
    professiondb.username_update = user.username
    return ProfessionService.update(item=professiondb)

@router.delete("/{id}",  status_code=status.HTTP_200_OK)
async def delete_profession(
    id: PyObjectId, user: UserInDB = Depends(get_actual_user)
):
    """Delete a profession by ID."""
    ProfessionService.delete(id=id)