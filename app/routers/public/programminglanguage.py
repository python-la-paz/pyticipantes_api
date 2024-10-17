from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.auth.access import get_api_key_public
from app.models import Result, Token, ProgrammingLanguage
from app.services import ProgrammingLanguageService

router = APIRouter()

@router.get(
    "",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_200_OK: {"model": List[ProgrammingLanguage]},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def get_programming_languages(user: Token = Depends(get_api_key_public)):
    """Retrieve a list of programming languages."""
    programming_languages = ProgrammingLanguageService.list()
    if not programming_languages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No programming languages found.")
    return programming_languages