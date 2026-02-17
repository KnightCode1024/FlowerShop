import logging
from collections.abc import Iterable
from contextlib import asynccontextmanager

from dishka import Provider, make_async_container
from fastapi import APIRouter, FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from clients import RedisClient
from entrypoint.config import Config, create_config

from core.broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = create_config()
    redis_client = RedisClient(config)
    redis = redis_client.get_redis()
    await redis.ping()
    logging.info("Redis is working")

    if not broker.is_worker_process:
        print("Starting broker")
        await broker.startup()
        print("Broker write_channel:", broker.write_channel)
        if broker.write_channel is None:
            print("❌ write_channel is None! RabbitMQ connection failed?")
        else:
            print("✅ write_channel is OK")

    print("Broker started, is_worker_process =", broker.is_worker_process)
    print(f"Broker connection: {broker.write_conn}")

    yield

    print("Broker started, is_worker_process =", broker.is_worker_process)
    print(f"Broker connection: {broker.write_conn}")

    if not broker.is_worker_process:
        print("Stoping broker")
        await broker.shutdown()

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
