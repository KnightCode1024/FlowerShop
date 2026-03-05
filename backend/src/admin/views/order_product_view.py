from sqladmin import ModelView

from models.order import OrderProduct


class OrderProductAdmin(ModelView, model=OrderProduct):
    name = "Позиция заказа"
    name_plural = "Позиции заказа"
    icon = "fa-solid fa-box"
    column_labels = {
        "id": "ID",
        "order_id": "Заказ",
        "product_id": "Товар",
        "quantity": "Количество",
        "price": "Цена",
    }

    column_list = [
        OrderProduct.id,
        OrderProduct.order_id,
        OrderProduct.product_id,
        OrderProduct.quantity,
        OrderProduct.price,
    ]
    column_sortable_list = [OrderProduct.id, OrderProduct.order_id]
    form_columns = [
        OrderProduct.order_id,
        OrderProduct.product_id,
        OrderProduct.quantity,
        OrderProduct.price,
    ]
