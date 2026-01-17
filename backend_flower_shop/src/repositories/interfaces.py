from typing import Protocol

from fastapi import UploadFile

from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductFilterParams,
    ProductResponse,
    ProductsListResponse,
)
from schemas.category import CategoryCreate, CategoryUpdate


class ProductRepositoryInterface(Protocol):
    async def create(self, data: ProductCreate) -> ProductResponse: ...

    async def get_by_id(self, product_id: int) -> ProductResponse | None: ...

    async def get_filtered(
        self,
        filters: ProductFilterParams,
    ) -> list[ProductsListResponse]: ...

    async def update(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> ProductResponse | None: ...

    async def delete(self, product_id: int) -> int: ...

    async def exists_by_name(
        self, name: str, exclude_id: int | None = None
    ) -> bool: ...


class CategoryRepositoryInterface(Protocol):
    async def create(self, data: CategoryCreate): ...

    async def get_by_id(self, category_id: int): ...

    async def get_all(self, offset: int = 0, limit: int = 20) -> list: ...

    async def update(self, category_id: int, data: CategoryUpdate): ...

    async def delete(self, category_id: int): ...

    async def exists_by_name(
        self, name: str, exclude_id: int | None = None
    ) -> bool: ...


class ProductImageRepositoryInterface(Protocol):
    async def create_for_product(
        self, product_id: int, url: str, order: int, is_primary: bool
    ): ...

    async def delete_by_product_id(self, product_id: int): ...


class S3RepositoryInterface(Protocol):
    async def upload_image(self, file: UploadFile) -> str: ...

    async def delete_image(self, url: str) -> None: ...
