import logging
from collections.abc import Iterable
from contextlib import asynccontextmanager

from dishka import Provider, make_async_container
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from clients import RedisClient
from core import broker
from entrypoint.config import Config, create_config
from middlewares.metrics import MetricsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = create_config()
    redis_client = RedisClient(config)
    redis = redis_client.get_redis()
    await redis.ping()
    logging.info("Redis is working")

    await broker.startup()

    yield

    await broker.shutdown()

    await redis.aclose()
    logging.info("Redis disconnected")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app


def create_mock_app() -> FastAPI:
    app = FastAPI()
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
    # instrument = Instrumentator().instrument(app)
    # instrument.expose(app, endpoint="/metrics")

    app.add_middleware(MetricsMiddleware)
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )