from fastapi import FastAPI
from sqladmin import Admin

from src.flowershop_api.core.admins.admin import UserAdmin
from src.flowershop_api.entrypoint.ioc.database import session_factory


def register_admin_views(app: FastAPI):
    admin = Admin(app=app, session_maker=session_factory)

    admin.add_view(UserAdmin)
