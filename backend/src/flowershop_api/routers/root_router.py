from fastapi import APIRouter

from flowershop_api.routers import (
    dev_router,
    product_router,
    user_router,
    category_router,
)

root_router = APIRouter(prefix="/api", tags=["API"])

routers = [
    dev_router,
    product_router,
    user_router,
    category_router,
]

for router in routers:
    root_router.include_router(router)
