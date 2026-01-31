from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Dev Tools"], route_class=DishkaRoute)


@router.get("/ping")
async def pong():
    return {"msg": "pong"}
