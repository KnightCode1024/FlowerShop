from typing import List

from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend_flower_shop.src.core.dependencies import get_db_session
from backend_flower_shop.src.schemas.product import (
    ProductResponse,
    ProductsListResponse,
    ProductUpdateRequest,
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.get("/", response_model=List[ProductsListResponse])
async def get_all_products(
    offset: int = 0,
    limit: int = 20,
    min_price: Decimal = None,
    max_price: Decimal = None,
    category_id: int = None,
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.post("/")
async def create_product(
    product_data: str = Form(
        ...,
        description="JSON строка с данными товара",
    ),
    images: List[UploadFile] = File([]),
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdateRequest,
    images: List[UploadFile] = File([]),
    session: AsyncSession = Depends(get_db_session),
):
    return


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    return
