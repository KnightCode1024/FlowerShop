from decimal import Decimal

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from core.exceptions import (
    CategoryNotFoundError,
    ProductNotFoundError,
)
from schemas.product import (
    CreateProductRequest,
    ProductFilterParams,
    ProductResponse,
    ProductsListResponse,
    UpdateProductRequest,
)
from schemas.user import UserResponse
from services import ProductsService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    route_class=DishkaRoute,
)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    service: FromDishka[ProductsService],
    product_id: int,
):
    try:
        return await service.get_product(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")


@router.get("/", response_model=list[ProductsListResponse])
async def get_products(
    service: FromDishka[ProductsService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    category_id: int | None = Query(None, gt=0),
    in_stock: bool | None = Query(None),
):
    filters = ProductFilterParams(
        offset=offset,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        in_stock=in_stock,
    )

    try:
        return await service.get_products(filters)
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/", response_model=ProductResponse)
async def create_product(
    service: FromDishka[ProductsService],
    current_user: FromDishka[UserResponse],
    product_data: str = Form(...),
    images: list[UploadFile] = File([]),
):
    try:
        request = CreateProductRequest.model_validate_json(product_data)
        return await service.create_product(current_user, request, images)
    except (CategoryNotFoundError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    service: FromDishka[ProductsService],
    current_user: FromDishka[UserResponse],
    product_id: int,
    product_data: str = Form(...),
    images: list[UploadFile] = File([]),
):
    try:
        request = UpdateProductRequest.model_validate_json(product_data)
        return await service.update_product(
            product_id,
            current_user,
            request,
            images,
        )
    except (ProductNotFoundError, CategoryNotFoundError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{product_id}")
async def delete_product(
    service: FromDishka[ProductsService],
    current_user: FromDishka[UserResponse],
    product_id: int,
):
    try:
        await service.delete_product(product_id, current_user)
        return {"message": "Product deleted successfully"}
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
