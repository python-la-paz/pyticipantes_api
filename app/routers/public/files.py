from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.auth.access import get_api_key_public
from app.models import Gender, Result, Token, UserAPI
from app.services.bl import UserProfileService
from app.utils import google_cloud_storage

router = APIRouter()

@router.get(
    "/{filename}",
)
async def get_file(filename:str, user: Token = Depends(get_api_key_public)):
    image, mime = google_cloud_storage.get_file(filename)
    if image is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Result(message="Imagen no encontrada").model_dump(),
        )
    image_stream = BytesIO(image)
    return StreamingResponse(image_stream, media_type=mime)
