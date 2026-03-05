from sqladmin import ModelView

from models.promocode import PromocodeAction


class PromocodeActionAdmin(ModelView, model=PromocodeAction):
    name = "Активация промокода"
    name_plural = "Активации промокодов"
    icon = "fa-solid fa-receipt"
    column_labels = {
        "promo_id": "Промокод",
        "user_id": "Пользователь",
    }

    column_list = [
        PromocodeAction.promo_id,
        PromocodeAction.user_id,
    ]
    form_columns = [
        PromocodeAction.promo_id,
        PromocodeAction.user_id,
    ]
