from fastapi import FastAPI
from sqladmin import Admin

from admin.auth import JWTAdminAuth
from admin.views import (
    CategoryAdmin,
    InvoiceAdmin,
    OrderAdmin,
    OrderProductAdmin,
    ProductAdmin,
    ProductImageAdmin,
    PromocodeActionAdmin,
    PromocodeAdmin,
    UserAdmin,
)
from entrypoint.config import config
from entrypoint.ioc.engine import session_factory


def create_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app=app,
        session_maker=session_factory,
        authentication_backend=JWTAdminAuth(secret_key=config.app.NAME),
    )
    register_admin_views(admin)
    return admin


def register_admin_views(admin: Admin) -> None:
    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(OrderProductAdmin)
    admin.add_view(PromocodeAdmin)
    admin.add_view(PromocodeActionAdmin)
    admin.add_view(InvoiceAdmin)
