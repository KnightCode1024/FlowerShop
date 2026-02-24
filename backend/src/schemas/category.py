from pydantic import BaseModel, Field


class CategoryProductResponse(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    price: float = Field(..., ge=0)
    in_stock: bool = Field(True)
    main_image_url: str | None = Field(None)


class CategoryBase(BaseModel):
    id: int = Field(...)
    name: str = Field(..., max_length=255)


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=255)


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)


class CategoryResponse(CategoryBase):
    id: int
    name: str
    products: list[CategoryProductResponse] = Field(default_factory=list)


class CategoryCreateResponse(CategoryBase):
    pass


class CategoryOneProductResponse(CategoryBase):
    pass


class CategoriesListResponse(CategoryBase):
    products_count: int = Field(0, ge=0)
