from typing import List
from decimal import Decimal

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy import select

from repositories.base import BaseRepository
from models import Product, ProductImage, Category
from services.s3_service import S3Service


class ProductRepository(BaseRepository):
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            Product,
            session,
        )
        self.s3_sevice = S3Service()

    async def create_product(
        self,
        product_data: dict,
        images: List[UploadFile],
    ):
        product = Product(**dict(product_data))
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        print(f"Product created with ID: {product.id}")

        if images:
            try:
                urls = await self.s3_sevice.upload_images(images, product.id)
                for i, url in enumerate(urls):
                    product_image = ProductImage(
                        product_id=product.id,
                        url=url,
                        order=i,
                        is_primary=(i == 0),
                    )
                    self.session.add(product_image)
                    print(f"Created image record: {url}")

                await self.session.commit()

            except Exception as e:
                print(f"Error uploading images: {e}")

        await self.session.refresh(product)

        return product

    async def get_all_products(
        self,
        offset: int = 0,
        limit: int = 20,
        min_price: Decimal = None,
        max_price: Decimal = None,
        category_id: int = None,
    ):
        subquery = (
            select(ProductImage).where(ProductImage.is_primary == True).subquery()
        )

        stmt = (
            select(Product, subquery.c.url.label("main_image_url"), Category.name.label("category_name"))
            .join(Category, Product.category_id == Category.id)
            .outerjoin(
                subquery,
                Product.id == subquery.c.product_id,
            )
            .offset(offset)
            .limit(limit)
        )
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        result = await self.session.execute(stmt)
        products = result.all()

        products_list = []
        for product, main_image_url, category_name in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "in_stock": product.in_stock,
                "category_id": product.category_id,
                "main_image_url": main_image_url,
                "category_name": category_name,
            }
            products_list.append(product_dict)

        return products_list

    async def get_product_with_details(self, product_id: int):
        stmt = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.images)
            )
            .where(Product.id == product_id)
        )

        result = await self.session.execute(stmt)
        product = result.unique().scalar_one_or_none()

        if product is None:
            return None

        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "in_stock": product.in_stock,
            "category_id": product.category_id,
            "images": [
                {
                    "id": img.id,
                    "url": img.url,
                    "order": img.order,
                    "is_primary": img.is_primary
                }
                for img in product.images
            ],
            "category": {
                "id": product.category.id,
                "name": product.category.name
            } if product.category else None
        }

    async def delete_product_with_images(self, product_id: int, s3_service):


        stmt = (
            select(Product)
            .options(joinedload(Product.images))
            .where(Product.id == product_id)
        )

        result = await self.session.execute(stmt)
        product = result.unique().scalar_one_or_none()

        if not product:
            return False

        image_urls = [image.url for image in product.images]

        if image_urls:
            deleted_count = await s3_service.delete_images(image_urls)
            print(f"Deleted {deleted_count} images from S3 for product {product_id}")

        await self.session.delete(product)
        await self.session.commit()
        return True

    async def update_product_with_images(self, product_id: int, update_data: dict, new_images: List[UploadFile] = None, s3_service = None):
        product = await self.get(product_id)
        if not product:
            return None

        for field, value in update_data.items():
            if value is not None and hasattr(product, field):
                setattr(product, field, value)

        if new_images and s3_service:
            old_image_urls = [img.url for img in product.images]
            if old_image_urls:
                await s3_service.delete_images(old_image_urls)

            for image in product.images:
                await self.session.delete(image)

            if new_images:
                new_image_urls = await s3_service.upload_images(new_images, product_id)

                for i, url in enumerate(new_image_urls):
                    new_image = ProductImage(
                        product_id=product_id,
                        url=url,
                        order=i,
                        is_primary=(i == 0),
                    )
                    self.session.add(new_image)

        await self.session.commit()
        await self.session.refresh(product)

        return product
