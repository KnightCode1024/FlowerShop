import logging

from dishka import AsyncContainer, Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from admins import create_admin
from entrypoint.ioc.registry import get_providers
from entrypoint.setup import (configure_app, configure_middlewares, create_app,
                              create_async_container)
from routers.root_router import root_router

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def make_app(*di_providers: Provider) -> FastAPI:
    app: FastAPI = create_app()

    configure_middlewares(app=app)

    configure_app(app=app, root_router=root_router)

    providers = get_providers()

    async_container: AsyncContainer = create_async_container(
        [
            *providers,
            *di_providers,
        ]
    )
    setup_dishka(container=async_container, app=app)

    create_admin(app)

    return app
