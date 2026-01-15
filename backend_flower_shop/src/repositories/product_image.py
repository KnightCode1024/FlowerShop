from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models import ProductImage


class ProductImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> ProductImage:
        image = ProductImage(**data)
        self.session.add(image)
        return image

    async def get_by_id(self, image_id: int) -> ProductImage | None:
        query = select(ProductImage).where(ProductImage.id == image_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_product_id(self, product_id: int) -> List[ProductImage]:
        query = (
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.order)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_for_product(
        self, product_id: int, url: str, order: int, is_primary: bool = False
    ) -> ProductImage:
        image_data = {
            "product_id": product_id,
            "url": url,
            "order": order,
            "is_primary": is_primary,
        }
        return await self.create(image_data)

    async def update(self, image_id: int, data: dict) -> ProductImage | None:
        image = await self.get_by_id(image_id)
        if not image:
            return None

        for key, value in data.items():
            setattr(image, key, value)

        self.session.add(image)
        return image

    async def delete(self, image_id: int) -> bool:
        image = await self.get_by_id(image_id)
        if not image:
            return False

        await self.session.delete(image)
        return True

    async def delete_by_product_id(self, product_id: int) -> int:
        query = delete(ProductImage).where(
            ProductImage.product_id == product_id,
        )
        result = await self.session.execute(query)
        return result.rowcount
