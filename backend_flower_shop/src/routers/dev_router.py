from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Dev Tools"])


@router.get("/ping")
async def pong():
    return {"msg": "pong"}
