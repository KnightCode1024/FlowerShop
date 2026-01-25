from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute

router = APIRouter(prefix="", tags=["Dev Tools"], route_class=DishkaRoute)


@router.get("/ping")
async def pong():
    return {"msg": "pong"}
