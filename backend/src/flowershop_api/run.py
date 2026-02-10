from dishka import AsyncContainer, Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqladmin import Admin

from src.flowershop_api.core.admins import register_admin_views
from src.flowershop_api.entrypoint.ioc.database import session_factory
from src.flowershop_api.entrypoint.ioc.registry import get_providers
from src.flowershop_api.entrypoint.setup import (configure_app, create_app,
                                                 create_async_container)
from src.flowershop_api.routers.root_router import root_router


def make_app(*di_providers: Provider) -> FastAPI:
    app: FastAPI = create_app()

    configure_app(app=app, root_router=root_router)

    async_container: AsyncContainer = create_async_container(
        [
            *get_providers(),
            *di_providers,
        ]
    )
    setup_dishka(container=async_container, app=app)

    register_admin_views(app=app)

    return app
