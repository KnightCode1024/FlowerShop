from sqladmin import ModelView

from models import User


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_labels = {
        "id": "ID",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "email": "Email",
        "username": "Имя пользователя",
        "role": "Роль",
        "email_verified": "Email подтвержден",
    }

    column_list = [
        User.id,
        User.created_at,
        User.updated_at,
        User.email,
        User.username,
        User.role,
        User.email_verified,
    ]
    column_searchable_list = [
        User.email,
        User.username,
    ]
    column_sortable_list = [
        User.id,
        User.created_at,
        User.updated_at,
        User.email,
    ]

    form_columns = [
        User.email,
        User.username,
        User.role,
        User.email_verified,
    ]
