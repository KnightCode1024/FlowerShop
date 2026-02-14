import logging
from collections.abc import Iterable
from contextlib import asynccontextmanager

from dishka import Provider, make_async_container
from fastapi import APIRouter, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from clients import RedisClient
from entrypoint.config import Config, create_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = create_config()
    redis_client = RedisClient(config)
    redis = redis_client.get_redis()
    await redis.ping()
    logging.info("Redis is working")

    yield
    await redis.aclose()
    logging.info("Redis disconnected")



def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app


def create_async_container(providers: Iterable[Provider]):
    config = create_config()
    return make_async_container(
        *providers,
        context={Config: config},
    )


def configure_app(app: FastAPI, root_router: APIRouter) -> None:
    app.include_router(root_router)


def configure_middlewares(app: FastAPI) -> None:
    instrument = Instrumentator().instrument(app)
    instrument.expose(app, endpoint="/metrics")
