from typing import List
from fastapi import UploadFile

from core.uow import UnitOfWork

from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductsListResponse,
    ProductFilterParams,
    CreateProductRequest,
    UpdateProductRequest,
)
from core.exceptions import (
    ProductNotFoundError,
    CategoryNotFoundError,
    ProductNameNotUniqueError,
)


class ProductsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_product(self, product_id: int) -> ProductResponse:
        product = await self.uow.products.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return product

    async def get_products(
        self, filters: ProductFilterParams
    ) -> List[ProductsListResponse]:
        if filters.category_id:
            category = await self.uow.categories.get_by_id(filters.category_id)
            if not category:
                raise CategoryNotFoundError(filters.category_id)

        products = await self.uow.products.get_filtered(filters)
        return products

    async def create_product(
        self,
        request: CreateProductRequest,
        images: List[UploadFile] | None = None,
    ) -> ProductResponse:
        await self._validate_category_exists(request.category_id)
        await self._validate_product_name_unique(request.name)

        async with self.uow:
            product_data = ProductCreate(**request.model_dump())
            product = await self.uow.products.create(product_data)

            images_to_create = images or getattr(request, "images", None)
            if images_to_create:
                for i, image_file in enumerate(images_to_create):
                    image_url = await self.uow.s3.upload_image(image_file)
                    await self.uow.images.create_for_product(
                        product_id=product.id,
                        url=image_url,
                        order=i,
                        is_primary=(i == 0),
                    )

        return product

    async def update_product(
        self,
        product_id: int,
        request: UpdateProductRequest,
        new_images: List[UploadFile] | None = None,
    ) -> ProductResponse:

        existing_product = await self.uow.products.get_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundError(product_id)

        if request.category_id:
            await self._validate_category_exists(request.category_id)

        if request.name and request.name != existing_product.name:
            await self._validate_product_name_unique(
                request.name, exclude_id=product_id
            )

        async with self.uow:
            update_data = ProductUpdate(**request.model_dump())
            product = await self.uow.products.update(product_id, update_data)

            images_to_create = new_images or getattr(
                request,
                "new_images",
                None,
            )
            if images_to_create:
                for i, image_file in enumerate(images_to_create):
                    image_url = await self.uow.s3.upload_image(image_file)
                    await self.uow.images.create_for_product(
                        product_id=product_id,
                        url=image_url,
                        order=i,
                        is_primary=(i == 0),
                    )

        return product

    async def delete_product(self, product_id: int) -> None:
        async with self.uow:
            product = await self.uow.products.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError(product_id)

            if product.images:
                for image in product.images:
                    await self.uow.s3.delete_image(image.url)

            await self.uow.images.delete_by_product_id(product_id)
            await self.uow.products.delete(product_id)

    async def _validate_category_exists(self, category_id: int) -> None:
        category = await self.uow.categories.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)

    async def _validate_product_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> None:
        exists = await self.uow.products.exists_by_name(name, exclude_id)
        if exists:
            raise ProductNameNotUniqueError(name)
