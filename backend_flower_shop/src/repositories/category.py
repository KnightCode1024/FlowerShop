from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Category, Product
from schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        data: CategoryCreate,
    ) -> Category:
        category = Category(**data.model_dump())
        self.session.add(category)
        return category

    async def get_by_id(
        self,
        category_id: int,
    ) -> Category | None:
        query = (
            select(Category)
            .outerjoin(Product, Product.category_id == Category.id)
            .options(joinedload(Category.products))
            .where(Category.id == category_id)
            .distinct(Category.id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Category]:
        query = (
            select(Category)
            .outerjoin(Product, Product.category_id == Category.id)
            .options(joinedload(Category.products))
            .distinct(Category.id)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def update(
        self,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category | None:
        category = await self._get_category_base(category_id)
        if not category:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)

        self.session.add(category)
        return category

    async def delete(
        self,
        category_id: int,
    ) -> Category | None:
        category = await self._get_category_base(category_id)
        if not category:
            return None

        await self.session.delete(category)
        return category

    async def exists_by_name(
        self,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:
        query = select(Category).where(Category.name == name)
        if exclude_id is not None:
            query = query.where(Category.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _get_category_base(
        self,
        category_id: int,
    ) -> Category | None:
        query = select(Category).where(Category.id == category_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
