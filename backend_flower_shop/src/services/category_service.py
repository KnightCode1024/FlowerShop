from typing import List
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import CategoryRepository
from models import Category, Product, ProductImage


class CategoryService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(
        self,
        category_data: dict,
    ):
        category = await self.category_repo.create(category_data)
        return {
            "id": category.id,
            "name": category.name,
        }

    async def get_category(self, category_id: int):
        stmt = (
            select(Category)
            .options(
                joinedload(Category.products)
                .joinedload(Product.images)
            )
            .where(Category.id == category_id)
        )

        result = await self.session.execute(stmt)
        category = result.unique().scalar_one_or_none()

        if not category:
            return None


        products_data = []
        for product in category.products:
            main_image = next(
                (img for img in product.images if img.is_primary),
                product.images[0] if product.images else None
            )
            main_image_url = main_image.url if main_image else None

            product_data = {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "in_stock": product.in_stock,
                "main_image_url": main_image_url,
            }
            products_data.append(product_data)

        return {
            "id": category.id,
            "name": category.name,
            "products": products_data,
        }

    async def get_all_categories(
        self,
        offset: int = 0,
        limit: int = 20,
    ):
        return await self.category_repo.get_all_categories(
            offset,
            limit,
        )

    async def delete_category(self, category_id: int):
        return await self.category_repo.delete(category_id)

    async def update_category(self, category_id: int, category_data: dict):
        return await self.category_repo.update(category_id, category_data)
