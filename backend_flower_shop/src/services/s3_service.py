import uuid
from pathlib import Path
from typing import List

from fastapi import UploadFile

from core.config import config
from core.s3_client import S3Client


class S3Service:
    def __init__(self):
        self.s3_client = S3Client(
            access_key=config.s3.ACCESS_KEY,
            secret_key=config.s3.SECRET_KEY,
            endpoint_url=config.s3.ENDPOINT,
            bucket_name=config.s3.BUCKET_NAME,
        )

    async def upload_image(
        self,
        image: UploadFile,
        product_id: int,
    ) -> str:
        file_extention = Path(image.filename).suffix
        s3_key = f"products/{product_id}/{uuid.uuid4()}{file_extention}"

        async with self.s3_client.get_client() as client:
            content = await image.read()

            await client.put_object(
                Bucket=self.s3_client.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=image.content_type,
            )

        url = f"{config.s3.PUBLIC_ENDPOINT}/{config.s3.BUCKET_NAME}/{s3_key}"

        return url

    async def upload_images(
        self,
        images: List[UploadFile],
        product_id: int,
    ) -> List[str]:
        urls = []
        for image in images:
            image_url = await self.upload_image(image, product_id)
            urls.append(image_url)

        return urls

    async def delete_image(self, image_url: str) -> bool:
        try:
            url_parts = image_url.split('/')
            bucket_index = url_parts.index(self.s3_client.bucket_name)
            s3_key = '/'.join(url_parts[bucket_index + 1:])

            async with self.s3_client.get_client() as client:
                await client.delete_object(
                    Bucket=self.s3_client.bucket_name,
                    Key=s3_key
                )
            return True
        except Exception as e:
            print(f"Error deleting image {image_url}: {e}")
            return False

    async def delete_images(self, image_urls: List[str]) -> int:
        deleted_count = 0
        for image_url in image_urls:
            if await self.delete_image(image_url):
                deleted_count += 1
        return deleted_count