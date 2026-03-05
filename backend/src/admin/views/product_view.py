import inspect

from fastapi import UploadFile
from sqlalchemy.orm import object_session
from sqladmin import ModelView
from wtforms.fields import MultipleFileField

from models import Product, ProductImage
from repositories.product_image import ProductImageRepository
from repositories.s3 import S3Repository


class ProductAdmin(ModelView, model=Product):
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-seedling"
    column_labels = {
        "id": "ID",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "name": "Название",
        "description": "Описание",
        "price": "Цена",
        "in_stock": "В наличии",
        "category": "Категория",
        "image_files": "Фотографии",
    }

    column_list = [
        Product.id,
        Product.created_at,
        Product.updated_at,
        Product.name,
        Product.price,
        Product.in_stock,
        Product.category,
    ]
    column_searchable_list = [Product.name, Product.description]
    column_sortable_list = [Product.id, Product.created_at, Product.price]

    form_columns = [
        Product.name,
        Product.description,
        Product.price,
        Product.in_stock,
        Product.category,
    ]
    form_extra_fields = {
        "image_files": MultipleFileField("Фотографии товара"),
    }
    form_create_rules = [
        "name",
        "description",
        "price",
        "in_stock",
        "category",
        "image_files",
    ]
    form_edit_rules = form_create_rules

    async def on_model_change(self, data, model, is_created, request):
        await self._ensure_product_id(model)

        file_objects = data.get("image_files")
        if not file_objects:
            form_data = await request.form()
            file_objects = form_data.getlist("image_files")

        if not file_objects:
            return

        if not isinstance(file_objects, (list, tuple)):
            file_objects = [file_objects]

        files: list[UploadFile] = []
        for file_obj in file_objects:
            if not file_obj or not getattr(file_obj, "filename", None):
                continue
            if not isinstance(file_obj, UploadFile):
                file_obj = UploadFile(
                    filename=file_obj.filename,
                    file=file_obj.file,
                    headers=getattr(file_obj, "headers", None),
                )
            files.append(file_obj)

        if not files:
            return
        if not getattr(model, "id", None):
            raise ValueError(
                "Нельзя загрузить фотографии, пока товар не сохранен."
            )

        s3_repo = S3Repository()
        image_repo = self._get_image_repository(model)
        existing_images = list(getattr(model, "images", []) or [])
        next_order = max((img.order for img in existing_images), default=-1) + 1
        has_primary = any(img.is_primary for img in existing_images)
        uploaded_urls = await s3_repo.upload_images(files, model.id)

        for uploaded_url in uploaded_urls:
            is_primary = not has_primary
            if image_repo:
                await image_repo.create_for_product(
                    product_id=model.id,
                    url=uploaded_url,
                    order=next_order,
                    is_primary=is_primary,
                )
            else:
                model.images.append(
                    ProductImage(
                        url=uploaded_url,
                        order=next_order,
                        is_primary=is_primary,
                    ),
                )
            if is_primary:
                has_primary = True
            next_order += 1

    async def _ensure_product_id(self, model: Product) -> None:
        if getattr(model, "id", None):
            return

        session = object_session(model)
        if session is None:
            return

        flushed = session.flush()
        if inspect.isawaitable(flushed):
            await flushed

    def _get_image_repository(
        self,
        model: Product,
    ) -> ProductImageRepository | None:
        session = object_session(model)
        if session is None:
            return None
        return ProductImageRepository(session)
