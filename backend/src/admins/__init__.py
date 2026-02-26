from fastapi import FastAPI
from sqladmin import Admin

from admins.views import UserAdmin, ProductAdmin, OrderAdmin, CategoryAdmin
from entrypoint.ioc.engine import session_factory


def create_admin(
    app: FastAPI,
) -> Admin:
    admin = Admin(app=app, session_maker=session_factory)

    register_admin_views(admin)

    return admin


def register_admin_views(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(CategoryAdmin)
