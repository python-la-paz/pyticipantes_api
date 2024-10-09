from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse, JSONResponse

from app.models import Page, Result
from app.services.page import PageService

router = APIRouter()


@router.get("/{slug}", response_model=Page, status_code=status.HTTP_200_OK)
async def get_page(slug: str):
    """Get a page by slug and return HTMLResponse

    Args:
        slug (str): Page slug to search in database
    """
    search = PageService.get_by_slug(slug=slug)
    if search is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Result(message="Page not Found").model_dump(),
        )
    else:
        return search
