from typing import Optional

# from decimal import Decimal
# from datetime import datetime

from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    url: str = Field(
        ...,
        max_length=1000,
        description="URL изображения",
    )

    order: int = Field(
        default=0,
        ge=0,
        description="Порядок изображения",
    )
    is_primary: bool = Field(
        default=False,
        description="Основное изображение",
    )


class ProductImageResponse(ProductImageBase):
    pass


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    order: Optional[int] = Field(
        None,
        ge=0,
        description="Порядок изображения",
    )
    is_primary: Optional[bool] = Field(
        None,
        description="Основное изображение",
    )
