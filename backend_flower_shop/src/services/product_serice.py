from typing import List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from repositories import ProductRepository
from services.s3_service import S3Service
from schemas.product_schema import ProductUpdateRequest


class ProductService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.s3_service = S3Service()

    async def create_product(
        self,
        product_data: dict,
        images: List[UploadFile],
    ):
        return await self.product_repo.create_product(
            product_data,
            images,
        )

    async def get_product(self, product_id: int):
        return await self.product_repo.get_product_with_details(product_id)

    async def get_all_products(
        self,
        offset: int = 0,
        limit: int = 20,
        min_price: Decimal = None,
        max_price: Decimal = None,
        category_id: int = None,
    ):
        return await self.product_repo.get_all_products(
            offset,
            limit,
            min_price,
            max_price,
            category_id,
        )

    async def delete_product(self, product_id: int):
        return await self.product_repo.delete_product_with_images(product_id, self.s3_service)

    async def update_product(self, product_id: int, update_data: ProductUpdateRequest, new_images: List[UploadFile] = None):
        update_dict = update_data.model_dump(exclude_unset=True)
        return await self.product_repo.update_product_with_images(product_id, update_dict, new_images, self.s3_service)
