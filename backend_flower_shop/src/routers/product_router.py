from typing import List
import json
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from core.dependencies.db import get_db_session
from schemas.product_schema import (
    ProductCreate,
    ProductResponse,
    ProductsListResponse,
    ProductUpdateRequest,
)

from services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    product_service = ProductService(session)
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    return product


@router.get("/", response_model=List[ProductsListResponse])
async def get_all_products(
    offset: int = 0,
    limit: int = 20,
    min_price: Decimal = None,
    max_price: Decimal = None,
    category_id: int = None,
    session: AsyncSession = Depends(get_db_session),
):
    if min_price is not None and max_price is not None and max_price <= min_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Максимальная цена должна быть больше минимальной",
        )

    product_service = ProductService(session)
    return await product_service.get_all_products(
        offset,
        limit,
        min_price,
        max_price,
        category_id,
    )


@router.post("/")
async def create_product(
    product_data: str = Form(
        ...,
        description="JSON строка с данными товара",
    ),
    images: List[UploadFile] = File([]),
    session: AsyncSession = Depends(get_db_session),
):
    for i, img in enumerate(images):
        print(f"Router, Image {i}: {img.filename}, size: {img.size}")

    try:
        product_dict = json.loads(product_data)
        product_obj = ProductCreate(**product_dict)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Некоректный JSON в product_data",
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e,
        )
    product_service = ProductService(session)
    return await product_service.create_product(product_obj, images)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdateRequest,
    images: List[UploadFile] = File([]),
    session: AsyncSession = Depends(get_db_session),
):
    product_service = ProductService(session)
    updated_product = await product_service.update_product(product_id, product_data, images)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    return await product_service.get_product(product_id)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    product_service = ProductService(session)
    return await product_service.delete_product(product_id)
