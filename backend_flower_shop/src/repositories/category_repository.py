from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from repositories.base import BaseRepository
from models import Category, Product


class CategoryRepository(BaseRepository):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            Category,
            session,
        )

    async def get_all_categories(
        self,
        offset: int = 0,
        limit: int = 20,
    ):
        stmt = (
            select(
                Category,
                func.count(Product.id).label("products_count")
            )
            .outerjoin(Product, Category.id == Product.category_id)
            .group_by(Category.id)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        categories = result.all()

        categories_list = []
        for category, products_count in categories:
            category_dict = {
                "id": category.id,
                "name": category.name,
                "products_count": products_count or 0,
            }
            categories_list.append(category_dict)

        return categories_list
