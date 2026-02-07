from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.flowershop_api.schemas.order import OrderCreateRequest
from src.flowershop_api.schemas.user import UserResponse
from src.flowershop_api.services.order import OrdersService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    route_class=DishkaRoute
)


@router.post("/")
async def add_order(request_data: OrderCreateRequest,
                    current_user: FromDishka[UserResponse],
                    service: FromDishka[OrdersService]):
    return await service.create_order(current_user, request_data)


@router.patch("/{id}")
async def patch_order():
    pass

@router.delete("/{id}")
async def delete_order():
    pass


@router.get("/")
async def get_all_orders():
    pass
