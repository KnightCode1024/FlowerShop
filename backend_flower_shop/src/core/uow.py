from sqlalchemy.ext.asyncio import AsyncSession

from repositories.product import ProductRepository
from repositories.category import CategoryRepository
from repositories.product_image import ProductImageRepository
from repositories.s3 import S3Repository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.products = ProductRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.images = ProductImageRepository(self.session)
        self.s3 = S3Repository()

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        return False
