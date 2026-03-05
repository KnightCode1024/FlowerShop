from sqladmin import ModelView

from models.invoices import Invoice


class InvoiceAdmin(ModelView, model=Invoice):
    name = "Счет"
    name_plural = "Счета"
    icon = "fa-solid fa-file-invoice-dollar"
    column_labels = {
        "id": "ID",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "method": "Метод",
        "link": "Ссылка",
        "name": "Название",
        "order_id": "Заказ",
        "user_id": "Пользователь",
        "amount": "Сумма",
        "status": "Статус",
        "uid": "UID",
    }

    column_list = [
        Invoice.id,
        Invoice.created_at,
        Invoice.updated_at,
        Invoice.method,
        Invoice.name,
        Invoice.order_id,
        Invoice.user_id,
        Invoice.amount,
        Invoice.status,
    ]
    column_sortable_list = [Invoice.id, Invoice.created_at, Invoice.amount]
    column_searchable_list = [Invoice.name, Invoice.link]

    form_columns = [
        Invoice.method,
        Invoice.link,
        Invoice.name,
        Invoice.order_id,
        Invoice.user_id,
        Invoice.amount,
        Invoice.status,
    ]
