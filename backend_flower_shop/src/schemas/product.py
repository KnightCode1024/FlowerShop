from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


from backend_flower_shop.src.schemas.product_image import (
    ProductImageResponse,
)
from backend_flower_shop.src.schemas.category import (
    CategoryOneProductResponse,
)


class ProductBase(BaseModel):
    id: int = Field(
        ...,
        description="ID товара",
    )
    name: str = Field(
        ...,
        max_length=255,
        description="Наименование товара",
    )
    description: str = Field(
        ...,
        max_length=255,
        description="Описание товара",
    )
    price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Цена продукта",
    )
    in_stock: bool = Field(
        True,
        description="В наличии",
    )
    category_id: int = Field(
        ...,
        description="ID категории товара",
    )

    # @field_validator("price", mode="after")
    # @classmethod
    # def validate_price(cls, value):
    #     if isinstance(value, str):
    #         try:
    #             value = Decimal(value)
    #         except Exception:
    #             raise ValueError("Некорректаная цена")

    #     if value < 0:
    #         raise ValidationError("Цена не может быть отрицательной")
    #     if value.as_tuple().exponent < -2:
    #         raise ValidationError(
    #             "Цена должна быть не более 2 знаков после запятой",
    #         )


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        max_length=255,
        description="Наименование товара",
    )
    description: str = Field(
        ...,
        max_length=255,
        description="Описание товара",
    )
    price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Цена продукта",
    )
    in_stock: bool = Field(
        True,
        description="В наличии",
    )
    category_id: int = Field(
        ...,
        description="ID категории товара",
    )


class ProductUpdateRequest(BaseModel):
    name: str = Field(
        None,
        max_length=255,
        description="Наименование товара",
    )
    description: str = Field(
        None,
        max_length=255,
        description="Описание товара",
    )
    price: Decimal = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Цена продукта",
    )
    in_stock: bool = Field(
        None,
        description="В наличии",
    )
    category_id: int = Field(
        None,
        description="ID категории товара",
    )


class ProductResponse(ProductBase):
    images: List[ProductImageResponse]
    category: CategoryOneProductResponse


class ProductsListResponse(ProductBase):
    main_image_url: str | None = Field(
        None,
        description="Главное фото товара",
    )
    category_name: str = Field(
        ...,
        description="Название категории",
    )
