from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query, status

from schemas.category import (CategoriesListResponse, CategoryCreate,
                              CategoryCreateResponse, CategoryResponse,
                              CategoryUpdate)
from schemas.user import UserResponse
from services.category import (CategoryHasProductsError, CategoryNotFoundError,
                               CategoryService)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    route_class=DishkaRoute,
)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    service: FromDishka[CategoryService],
):
    try:
        return await service.get_category(category_id)
    except CategoryNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        ) from err


@router.get("/", response_model=list[CategoriesListResponse])
async def get_all_categories(
    service: FromDishka[CategoryService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await service.get_categories(offset=offset, limit=limit)


@router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    category_data: CategoryCreate,
    service: FromDishka[CategoryService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.create_category(category_data, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    service: FromDishka[CategoryService],
    current_user: FromDishka[UserResponse],
):
    try:
        return await service.update_category(
            category_id,
            category_data,
            current_user,
        )
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
    service: FromDishka[CategoryService],
    current_user: FromDishka[UserResponse],
):
    try:
        await service.delete_category(
            category_id,
            current_user,
        )
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
