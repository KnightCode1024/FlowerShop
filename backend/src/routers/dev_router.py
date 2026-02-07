from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request

from core.rate_limiter_factory import rate_limit

router = APIRouter(prefix="", tags=["Dev Tools"], route_class=DishkaRoute)


@router.get("/ping")
@rate_limit(endpoint="ping", max_requests=3, window_seconds=30)
async def pong(request: Request):
    return {"msg": "pong"}
