from sqladmin import ModelView

from models import Category


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-tags"
    column_labels = {
        "id": "ID",
        "created_at": "Создана",
        "updated_at": "Обновлена",
        "name": "Название",
    }

    column_list = [
        Category.id,
        Category.created_at,
        Category.updated_at,
        Category.name,
    ]
    column_searchable_list = [Category.name]
    column_sortable_list = [Category.id, Category.created_at, Category.name]

    form_columns = [Category.name]
