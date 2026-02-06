from src.flowershop_api.routers.category_router import router as category_router
from src.flowershop_api.routers.dev_router import router as dev_router
from src.flowershop_api.routers.product_router import router as product_router
from src.flowershop_api.routers.user_router import router as user_router
from src.flowershop_api.routers.order_router import router as order_router
__all__ = [
    "category_router",
    "dev_router",
    "product_router",
    "user_router",
    "order_router"
]
