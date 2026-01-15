from typing import List, Optional

from core.uow import UnitOfWork
from schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoriesListResponse,
)
from core.exceptions import (
    CategoryNotFoundError,
    CategoryHasProductsError,
    CategoryNameNotUniqueError,
)


class CategoriesService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_category(self, category_id: int) -> CategoryResponse:
        category = await self.uow.categories.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        products = getattr(category, "products", []) or []
        products_list = []
        for p in products:
            main_image = None
            imgs = getattr(p, "images", []) or []
            if imgs:
                primary = next(
                    (img for img in imgs if getattr(img, "is_primary", False)),
                    imgs[0],
                )
                main_image = getattr(primary, "url", None)

            products_list.append(
                {
                    "id": getattr(p, "id"),
                    "name": getattr(p, "name"),
                    "price": getattr(p, "price"),
                    "in_stock": getattr(p, "in_stock"),
                    "main_image_url": main_image,
                }
            )

        category_dict = {
            "id": getattr(category, "id"),
            "name": getattr(category, "name"),
            "products": products_list,
        }
        return CategoryResponse.model_validate(category_dict)

    async def get_categories(
        self, offset: int = 0, limit: int = 20
    ) -> List[CategoriesListResponse]:
        categories = await self.uow.categories.get_all(
            offset=offset,
            limit=limit,
        )
        result = []
        for category in categories:
            products_count = len(getattr(category, "products", []) or [])
            result.append(
                CategoriesListResponse.model_validate(
                    {
                        "id": getattr(category, "id"),
                        "name": getattr(category, "name"),
                        "products_count": products_count,
                    }
                )
            )
        return result

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        await self._validate_category_name_unique(data.name)

        async with self.uow:
            category = await self.uow.categories.create(data)

        return CategoryResponse.model_validate(
            {
                "id": getattr(category, "id"),
                "name": getattr(category, "name"),
                "products": [],
            }
        )

    async def update_category(
        self, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse:
        existing_category = await self.uow.categories.get_by_id(category_id)
        if not existing_category:
            raise CategoryNotFoundError(category_id)

        if data.name and data.name != existing_category.name:
            await self._validate_category_name_unique(
                data.name,
                exclude_id=category_id,
            )

        async with self.uow:
            category = await self.uow.categories.update(category_id, data)

        return CategoryResponse.model_validate(
            {
                "id": getattr(category, "id"),
                "name": getattr(category, "name"),
                "products": [],
            }
        )

    async def delete_category(self, category_id: int) -> None:
        async with self.uow:
            category = await self.uow.categories.get_by_id(category_id)
            if not category:
                raise CategoryNotFoundError(category_id)

            if category.products:
                raise CategoryHasProductsError(
                    category_id,
                    len(category.products),
                )

            await self.uow.categories.delete(category_id)

    async def _validate_category_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> None:
        exists = await self.uow.categories.exists_by_name(name, exclude_id)
        if exists:
            raise CategoryNameNotUniqueError(name)
