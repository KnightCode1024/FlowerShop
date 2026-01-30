from flowershop_api.core.uow import UnitOfWork
from flowershop_api.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoriesListResponse,
)
from flowershop_api.core.exceptions import (
    CategoryNotFoundError,
    CategoryHasProductsError,
    CategoryNameNotUniqueError,
)
from flowershop_api.repositories import CategoryRepositoryI


class CategoriesService:
    def __init__(
        self,
        uow: UnitOfWork,
        category_repository: CategoryRepositoryI,
    ):
        self.uow = uow
        self.categories = category_repository

    async def get_category(self, category_id: int) -> CategoryResponse:
        category = await self.categories.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        products = category.products or []
        products_list = []
        for p in products:
            main_image = None
            imgs = p.images or []
            if imgs:
                primary = next(
                    (img for img in imgs if img.is_primary),
                    imgs[0],
                )
                main_image = primary.url

            products_list.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "in_stock": p.in_stock,
                    "main_image_url": main_image,
                }
            )

        category_dict = {
            "id": category.id,
            "name": category.name,
            "products": products_list,
        }
        return CategoryResponse.model_validate(category_dict)

    async def get_categories(
        self, offset: int = 0, limit: int = 20
    ) -> list[CategoriesListResponse]:
        categories = await self.categories.get_all(
            offset=offset,
            limit=limit,
        )
        result = []
        for category in categories:
            products_count = len(category.products or [])
            result.append(
                CategoriesListResponse.model_validate(
                    {
                        "id": category.id,
                        "name": category.name,
                        "products_count": products_count,
                    }
                )
            )
        return result

    async def create_category(
        self,
        data: CategoryCreate,
    ) -> CategoryResponse:
        await self._validate_category_name_unique(data.name)

        async with self.uow:
            category = await self.categories.create(data)

        return CategoryResponse.model_validate(
            {
                "id": category.id,
                "name": category.name,
                "products": [],
            }
        )

    async def update_category(
        self, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse:
        existing_category = await self.categories.get_by_id(category_id)
        if not existing_category:
            raise CategoryNotFoundError(category_id)

        if data.name and data.name != existing_category.name:
            await self._validate_category_name_unique(
                data.name,
                exclude_id=category_id,
            )

        async with self.uow:
            category = await self.categories.update(category_id, data)

        return CategoryResponse.model_validate(
            {
                "id": category.id,
                "name": category.name,
                "products": [],
            }
        )

    async def delete_category(self, category_id: int) -> None:
        async with self.uow:
            category = await self.categories.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundError(category_id)

            if category.products:
                raise CategoryHasProductsError(
                    category_id,
                    len(category.products),
                )

            await self.categories.delete(category_id)

    async def _validate_category_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> None:
        exists = await self.categories.exists_by_name(name, exclude_id)
        if exists:
            raise CategoryNameNotUniqueError(name)
