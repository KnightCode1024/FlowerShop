from fastapi import APIRouter

from routers import (
    category_router,
    dev_router,
    product_router,
    user_router, order_router, promocode_router,
)

root_router = APIRouter(prefix="/api", tags=["API"])

routers = [
    dev_router,
    product_router,
    user_router,
    category_router,
    order_router,
    promocode_router
]

for router in routers:
    root_router.include_router(router)




