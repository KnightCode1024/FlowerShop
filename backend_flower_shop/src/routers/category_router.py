from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.db import get_db_session
from schemas.category_schema import (
    CategoryCreate,
    CategoryResponse,
    CategoryCreateResponse,
    CategoriesListResponse,
    CategoryUpdate,
)

from services import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    category_service = CategoryService(session)
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    return category


@router.get("/", response_model=List[CategoriesListResponse])
async def get_all_categories(
    offset: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_db_session),
):
    category_service = CategoryService(session)
    return await category_service.get_all_categories(
        offset,
        limit,
    )


@router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_db_session),
):
    category_service = CategoryService(session)
    return await category_service.create_category(category_data.model_dump())


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    category_service = CategoryService(session)
    updated_category = await category_service.update_category(
        category_id,
        category_data.model_dump(exclude_unset=True)
    )
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    return updated_category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    category_service = CategoryService(session)
    deleted = await category_service.delete_category(category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    return {"message": "Категория успешно удалена"}
