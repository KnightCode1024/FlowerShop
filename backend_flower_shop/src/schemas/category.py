from typing import List

from pydantic import BaseModel, Field


class CategoryProductResponse(BaseModel):
    id: int = Field(..., description="ID товара")
    name: str = Field(..., description="Название товара")
    price: float = Field(..., description="Цена товара")
    in_stock: bool = Field(True, description="В наличии")
    main_image_url: str | None = Field(None, description="Главное фото товара")


class CategoryBase(BaseModel):
    id: int = Field(
        ...,
        description="ID категории",
    )
    name: str = Field(
        ...,
        max_length=255,
        description="Наименование категории",
    )


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        max_length=255,
        description="Наименование категории",
    )


class CategoryUpdate(BaseModel):
    name: str = Field(
        ...,
        max_length=255,
        description="Наименование категории",
    )


class CategoryResponse(CategoryBase):
    products: List[CategoryProductResponse] = Field(
        default_factory=list,
        description="Список товаров в категории",
    )


class CategoryCreateResponse(CategoryBase):
    pass


class CategoryOneProductResponse(CategoryBase):
    pass


class CategoriesListResponse(CategoryBase):
    products_count: int = Field(
        0,
        description="Количество товаров в категории",
    )
