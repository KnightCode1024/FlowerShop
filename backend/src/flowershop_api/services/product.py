from fastapi import UploadFile, HTTPException, status

from flowershop_api.core.uow import UnitOfWork
from flowershop_api.repositories import (
    ProductRepositoryI,
    CategoryRepositoryI,
    ProductImageRepositoryI,
    S3RepositoryI,
)

from flowershop_api.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductsListResponse,
    ProductFilterParams,
    CreateProductRequest,
    UpdateProductRequest,
)
from flowershop_api.schemas.user import UserResponse
from flowershop_api.core.exceptions import (
    ProductNotFoundError,
    CategoryNotFoundError,
    ProductNameNotUniqueError,
)
from flowershop_api.models import RoleEnum


class ProductsService:
    def __init__(
        self,
        uow: UnitOfWork,
        product_repository: ProductRepositoryI,
        category_repository: CategoryRepositoryI,
        image_repository: ProductImageRepositoryI,
        s3_repository: S3RepositoryI,
    ):
        self.uow = uow
        self.products = product_repository
        self.categories = category_repository
        self.images = image_repository
        self.s3 = s3_repository

    async def get_product(self, product_id: int) -> ProductResponse:
        product = await self.products.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return product

    async def get_products(
        self, filters: ProductFilterParams
    ) -> list[ProductsListResponse]:
        if filters.category_id:
            category = await self.categories.get_by_id(filters.category_id)
            if not category:
                raise CategoryNotFoundError(filters.category_id)

        products = await self.products.get_filtered(filters)
        return products

    async def create_product(
        self,
        user: UserResponse,
        request: CreateProductRequest,
        images: list[UploadFile] | None = None,
    ) -> ProductResponse:
        if user.role not in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access rights.",
            )

        await self._validate_category_exists(request.category_id)
        await self._validate_product_name_unique(request.name)

        async with self.uow:
            product_data = ProductCreate(**request.model_dump())
            product = await self.products.create(product_data)

            if images:
                for i, image_file in enumerate(images):
                    image_url = await self.s3.upload_image(
                        image_file,
                        product.id,
                    )
                    await self.images.create_for_product(
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
        new_images: list[UploadFile] | None = None,
    ) -> ProductResponse:

        existing_product = await self.products.get_by_id(product_id)
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
            product = await self.products.update(product_id, update_data)

            images_to_create = new_images
            if images_to_create:
                for i, image_file in enumerate(images_to_create):
                    image_url = await self.s3.upload_image(
                        image_file,
                        product_id,
                    )
                    await self.images.create_for_product(
                        product_id=product_id,
                        url=image_url,
                        order=i,
                        is_primary=(i == 0),
                    )

        return product

    async def delete_product(self, product_id: int) -> None:
        async with self.uow:
            deleted = await self.products.delete(product_id)
            if not deleted:
                raise ProductNotFoundError(product_id)

    async def _validate_category_exists(self, category_id: int) -> None:
        category = await self.categories.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)

    async def _validate_product_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> None:
        exists = await self.products.exists_by_name(name, exclude_id)
        if exists:
            raise ProductNameNotUniqueError(name)
