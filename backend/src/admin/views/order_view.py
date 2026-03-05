from sqladmin import ModelView

from models.order import Order


class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-basket-shopping"
    column_labels = {
        "id": "ID",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "user_id": "Пользователь",
        "status": "Статус",
        "amount": "Сумма",
    }

    column_list = [
        Order.id,
        Order.created_at,
        Order.updated_at,
        Order.user_id,
        Order.status,
        Order.amount,
    ]
    column_sortable_list = [Order.id, Order.created_at, Order.amount]
    form_columns = [Order.user_id, Order.status, Order.amount]
