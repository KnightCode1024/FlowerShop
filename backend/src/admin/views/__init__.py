from admin.views.invoice_view import InvoiceAdmin
from admin.views.category_view import CategoryAdmin
from admin.views.order_product_view import OrderProductAdmin
from admin.views.order_view import OrderAdmin
from admin.views.promocode_action_view import PromocodeActionAdmin
from admin.views.promocode_view import PromocodeAdmin
from admin.views.product_image_view import ProductImageAdmin
from admin.views.product_view import ProductAdmin
from admin.views.user_view import UserAdmin

__all__ = [
    "UserAdmin",
    "ProductAdmin",
    "CategoryAdmin",
    "OrderAdmin",
    "OrderProductAdmin",
    "ProductImageAdmin",
    "PromocodeAdmin",
    "PromocodeActionAdmin",
    "InvoiceAdmin",
]
