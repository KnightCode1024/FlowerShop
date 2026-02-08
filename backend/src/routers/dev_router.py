from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request

from core.rate_limiter import RateLimiter, Strategy, rate_limit

router = APIRouter(prefix="", tags=["Dev Tools"], route_class=DishkaRoute)


@router.get("/ping")
@rate_limit(strategy=Strategy.IP, policy="1/s;2/m;3/h")
async def pong(
    request: Request,
    rate_limiter: FromDishka[RateLimiter],
):
    return {"msg": "pong"}
