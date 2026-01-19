from routers.category_router import router as category_router
from routers.dev_router import router as dev_router
from routers.product_router import router as product_router
from routers.user_router import router as user_router

__all__ = [
    "category_router",
    "dev_router",
    "product_router",
    "user_router",
]
