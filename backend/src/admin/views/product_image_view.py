from starlette.datastructures import UploadFile
from sqladmin import ModelView
from wtforms.fields import FileField

from repositories.s3 import S3Repository
from models import ProductImage


class ProductImageAdmin(ModelView, model=ProductImage):
    name = "Изображение товара"
    name_plural = "Изображения товаров"
    icon = "fa-solid fa-image"
    column_labels = {
        "id": "ID",
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "product": "Товар",
        "url": "Ссылка",
        "order": "Порядок",
        "is_primary": "Главное",
        "image_file": "Файл изображения",
    }

    column_list = [
        ProductImage.id,
        ProductImage.created_at,
        ProductImage.updated_at,
        ProductImage.product,
        ProductImage.url,
        ProductImage.order,
        ProductImage.is_primary,
    ]
    column_sortable_list = [ProductImage.id, ProductImage.created_at, ProductImage.order]
    column_searchable_list = [ProductImage.url]

    form_columns = [
        ProductImage.product,
        ProductImage.url,
        ProductImage.order,
        ProductImage.is_primary,
    ]
    form_extra_fields = {
        "image_file": FileField("Файл изображения"),
    }

    async def on_model_change(self, data, model, is_created, request):
        file_obj = data.get("image_file")
        if not file_obj:
            if is_created and not model.url:
                raise ValueError(
                    "Укажите ссылку на изображение или загрузите файл."
                )
            return

        product_id = model.product_id
        if not product_id and data.get("product"):
            product = data.get("product")
            product_id = getattr(product, "id", None)

        if not product_id:
            raise ValueError("Выберите товар перед загрузкой изображения.")

        if not isinstance(file_obj, UploadFile):
            return

        s3_repo = S3Repository()
        uploaded_url = await s3_repo.upload_image(file_obj, product_id)
        model.url = uploaded_url
