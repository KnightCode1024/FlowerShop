from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from schemas.order import OrderCreateRequest, OrderUpdateRequest
from schemas.user import UserResponse
from services.order import OrdersService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    route_class=DishkaRoute
)


@router.post("/")
async def add_order(order_data: OrderCreateRequest,
                    current_user: FromDishka[UserResponse],
                    service: FromDishka[OrdersService]):
    return await service.create_order(current_user, order_data)


@router.patch("/{id}")
async def patch_order(order_data: OrderUpdateRequest,
                      current_user: FromDishka[UserResponse],
                      service: FromDishka[OrdersService]):
    return await service.update_order(current_user, order_data)


@router.delete("/{id}")
async def delete_order(id: int,
                       current_user: FromDishka[UserResponse],
                       service: FromDishka[OrdersService]):
    return await service.delete_order(current_user)


@router.get("/")
async def get_all_orders():
    pass
