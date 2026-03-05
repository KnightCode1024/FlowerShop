from sqladmin import ModelView

from models.promocode import Promocode


class PromocodeAdmin(ModelView, model=Promocode):
    name = "Промокод"
    name_plural = "Промокоды"
    icon = "fa-solid fa-percent"
    column_labels = {
        "id": "ID",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "code": "Код",
        "percent": "Скидка (%)",
        "count_activation": "Активаций",
        "max_count_activators": "Лимит активаций",
    }

    column_list = [
        Promocode.id,
        Promocode.created_at,
        Promocode.updated_at,
        Promocode.code,
        Promocode.percent,
        Promocode.count_activation,
        Promocode.max_count_activators,
    ]
    column_sortable_list = [Promocode.id, Promocode.created_at, Promocode.percent]
    column_searchable_list = [Promocode.code]

    form_columns = [
        Promocode.code,
        Promocode.percent,
        Promocode.count_activation,
        Promocode.max_count_activators,
    ]
