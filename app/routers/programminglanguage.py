from typing import List
from fastapi import APIRouter, Depends, status

from app.auth.access import get_actual_user
from app.models import UserInDB, ProgrammingLanguage, ProgrammingLanguageInDB
from app.models.programminglanguage import ProgrammingLanguage
from app.services import ProgrammingLanguageService
from app.utils.mongo_validator import PyObjectId

router = APIRouter()

@router.get("", response_model=List[ProgrammingLanguage], status_code=status.HTTP_200_OK)
async def get_programming_languages(user: UserInDB = Depends(get_actual_user)):
    """Retrieve a list of programming languages."""
    return ProgrammingLanguageService.list()

@router.get("/{id}", response_model=ProgrammingLanguage, status_code=status.HTTP_200_OK)
async def get_programming_language_by_id(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Retrieve a programming language by ID."""
    programming_language = ProgrammingLanguageService.get(programming_language_id=id)
    if not programming_language:
        raise HTTPException(status_code=404, detail="Programming language not found") 
    return programming_language

@router.post("", response_model=ProgrammingLanguage, status_code=status.HTTP_201_CREATED)
async def create_programming_language(programming_language: ProgrammingLanguage, user: UserInDB = Depends(get_actual_user)):
    """Create a new programming language."""
    programming_language_db = ProgrammingLanguageInDB(**programming_language.model_dump(by_alias=True))
    programming_language_db.username_insert = user.username
    return ProgrammingLanguageService.insert(item=programming_language_db)

@router.put("/{id}", response_model=ProgrammingLanguage, status_code=status.HTTP_200_OK)
async def update_programming_language(
    id: PyObjectId, programming_language: ProgrammingLanguage, user: UserInDB = Depends(get_actual_user)
):
    """Update an existing programming language."""
    programming_language_db = ProgrammingLanguageInDB(**programming_language.model_dump(by_alias=True))
    programming_language_db.id = id
    programming_language_db.username_update = user.username
    return ProgrammingLanguageService.update(item=programming_language_db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_programming_language(id: PyObjectId, user: UserInDB = Depends(get_actual_user)):
    """Delete a programming language by ID."""
    ProgrammingLanguageService.delete(id=id)
    return None
