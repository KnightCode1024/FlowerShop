from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from starlette.responses import PlainTextResponse

from core.rate_limiter import RateLimiter, Strategy, rate_limit
from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    GCCollector,
    process_collector,
    PLATFORM_COLLECTOR,
    REGISTRY
)


router = APIRouter(
    prefix="",
    tags=["Dev Tools"],
    route_class=DishkaRoute,
)


@router.get("/ping")
@rate_limit(strategy=Strategy.IP, policy="10/s;100/m;1000/h")
async def pong(
        request: Request,
        rate_limiter: FromDishka[RateLimiter],
):
    return {"msg": "pong"}


@router.get("/metrics")
async def metrics():
    data = generate_latest(REGISTRY)
    return PlainTextResponse(content=data, media_type=CONTENT_TYPE_LATEST)
