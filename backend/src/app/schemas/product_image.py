from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    url: str = Field(..., max_length=1000)

    order: int = Field(default=0, ge=0)
    is_primary: bool = Field(default=False)


class ProductImageResponse(ProductImageBase):
    pass


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    order: int | None = Field(None, ge=0)
    is_primary: bool | None = Field(None)
