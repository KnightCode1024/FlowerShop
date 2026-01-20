from fastapi import APIRouter, HTTPException, Query, status
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from services.category import (
    CategoriesService,
    CategoryNotFoundError,
    CategoryHasProductsError,
)
from schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryCreateResponse,
    CategoriesListResponse,
    CategoryUpdate,
)
from schemas.user import UserResponse


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    route_class=DishkaRoute,
)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    service: FromDishka[CategoriesService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.get_category(category_id)
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


@router.get("/", response_model=list[CategoriesListResponse])
async def get_all_categories(
    service: FromDishka[CategoriesService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await service.get_categories(offset=offset, limit=limit)


@router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    category_data: CategoryCreate,
    service: FromDishka[CategoriesService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.create_category(category_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    service: FromDishka[CategoriesService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.update_category(category_id, category_data)
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    service: FromDishka[CategoriesService],
    current_user: FromDishka[UserResponse],
):
    try:
        await service.delete_category(category_id)
        return {"message": "Category deleted successfully"}
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    except CategoryHasProductsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
