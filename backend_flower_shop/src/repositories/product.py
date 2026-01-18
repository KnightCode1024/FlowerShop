from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import joinedload

from models import Product, ProductImage, Category
from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductFilterParams,
    ProductResponse,
    ProductsListResponse,
)


class ProductRepositoryI(Protocol):
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


class ProductRepository(ProductRepositoryI):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProductCreate) -> ProductResponse:
        product = Product(**data.model_dump())
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        query = (
            select(Product)
            .options(joinedload(Product.category), joinedload(Product.images))
            .where(Product.id == product.id)
        )
        result = await self.session.execute(query)
        product_with_relations = result.unique().scalar_one()
        return await self._to_product_response(product_with_relations)

    async def get_by_id(self, product_id: int) -> ProductResponse | None:
        product = await self._get_product_with_relations(product_id)
        if not product:
            return None
        return await self._to_product_response(product)

    async def get_filtered(
        self,
        filters: ProductFilterParams,
    ) -> list[ProductsListResponse]:
        conditions = []

        if filters.min_price is not None:
            conditions.append(Product.price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(Product.price <= filters.max_price)
        if filters.category_id is not None:
            conditions.append(Product.category_id == filters.category_id)
        if filters.in_stock is not None:
            conditions.append(Product.in_stock == filters.in_stock)

        query = (
            select(Product)
            .outerjoin(Category, Category.id == Product.category_id)
            .outerjoin(ProductImage, ProductImage.product_id == Product.id)
            .options(joinedload(Product.category), joinedload(Product.images))
            .distinct(Product.id)
            .offset(filters.offset)
            .limit(filters.limit)
        )

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        products = result.unique().scalars().all()

        list_result: list[ProductsListResponse] = []
        for product in products:
            main_image_url = None
            images = getattr(product, "images", []) or []
            if images:
                primary = next(
                    (
                        img
                        for img in images
                        if getattr(
                            img,
                            "is_primary",
                            False,
                        )
                    ),
                    images[0],
                )
                main_image_url = getattr(primary, "url", None)

            category_name = (
                getattr(product.category, "name", "")
                if getattr(product, "category", None)
                else ""
            )

            prod_dict = {
                "id": getattr(product, "id"),
                "name": getattr(product, "name"),
                "description": getattr(product, "description"),
                "price": getattr(product, "price"),
                "in_stock": getattr(product, "in_stock"),
                "category_id": getattr(product, "category_id"),
                "main_image_url": main_image_url,
                "category_name": category_name,
            }
            list_result.append(ProductsListResponse.model_validate(prod_dict))
        return list_result

    async def update(
        self,
        product_id: int,
        data: ProductUpdate,
    ) -> ProductResponse | None:
        product = await self._get_product_with_relations(product_id)
        if not product:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(product, field, value)

        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return await self._to_product_response(product)

    async def delete(self, product_id: int) -> ProductResponse | None:
        query = delete(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        return result.rowcount

    async def _get_product_with_relations(
        self,
        product_id: int,
    ) -> Product | None:
        query = (
            select(Product)
            .outerjoin(ProductImage, ProductImage.product_id == Product.id)
            .outerjoin(Category, Category.id == Product.category_id)
            .options(joinedload(Product.images), joinedload(Product.category))
            .where(Product.id == product_id)
            .distinct(Product.id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def exists_by_name(
        self,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:
        query = select(Product).where(Product.name == name)
        if exclude_id is not None:
            query = query.where(Product.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _get_product_base(self, product_id: int) -> Product | None:
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _to_product_response(self, product: Product) -> ProductResponse:
        images = getattr(product, "images", []) or []
        images_list = [
            {
                "url": img.url,
                "order": getattr(img, "order", 0),
                "is_primary": getattr(img, "is_primary", False),
            }
            for img in images
        ]

        category = getattr(product, "category", None)
        category_dict = (
            {
                "id": getattr(category, "id", None),
                "name": getattr(
                    category,
                    "name",
                    "",
                ),
            }
            if category
            else None
        )

        prod_dict = {
            "id": getattr(product, "id"),
            "name": getattr(product, "name"),
            "description": getattr(product, "description"),
            "price": getattr(product, "price"),
            "in_stock": getattr(product, "in_stock"),
            "category_id": getattr(product, "category_id"),
            "images": images_list,
            "category": category_dict,
        }
        return ProductResponse.model_validate(prod_dict)
