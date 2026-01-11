from typing import List

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryCreateResponse,
    CategoriesListResponse,
    CategoryUpdate,
)


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.get("/", response_model=List[CategoriesListResponse])
async def get_all_categories(
    offset: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    return
