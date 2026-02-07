from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request

from core.rate_limiter import rate_limit, RateLimiter

router = APIRouter(prefix="", tags=["Dev Tools"], route_class=DishkaRoute)


@router.get("/ping")
@rate_limit(endpoint="ping", max_requests=3, window_seconds=30)
async def pong(
    request: Request,
    rate_limiter: FromDishka[RateLimiter],
):
    return {"msg": "pong"}
