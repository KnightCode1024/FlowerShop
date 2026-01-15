from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


from schemas.product_image import ProductImageResponse
from schemas.category import CategoryOneProductResponse


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    in_stock: bool = Field(True)
    category_id: int = Field(...)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    in_stock: bool | None = Field(None)
    category_id: int | None = Field(None)


class ProductFilterParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    category_id: int | None = Field(None, gt=0)
    in_stock: bool | None = Field(None)


class CreateProductRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    in_stock: bool = Field(True)
    category_id: int = Field(...)


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    in_stock: bool | None = Field(None)
    category_id: int | None = Field(None)


class ProductResponse(BaseModel):
    id: int = Field(...)
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    in_stock: bool = Field(True)
    category_id: int = Field(...)

    images: List[ProductImageResponse]
    category: CategoryOneProductResponse


class ProductsListResponse(BaseModel):
    id: int = Field(...)
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=255)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    in_stock: bool = Field(True)
    category_id: int = Field(...)

    main_image_url: Optional[str] = Field(None)
    category_name: str = Field(...)
