from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from schemas.order import OrderCreateRequest, OrderUpdateRequest
from schemas.user import UserResponse
from services.order import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"], route_class=DishkaRoute)


@router.post("/")
async def add_order(
    order_data: OrderCreateRequest,
    current_user: FromDishka[UserResponse],
    service: FromDishka[OrderService],
):
    return await service.create_order(current_user, order_data)


@router.patch("/{id}")
async def patch_order(
    order_data: OrderUpdateRequest,
    current_user: FromDishka[UserResponse],
    service: FromDishka[OrderService],
):
    return await service.update_order(current_user, order_data)


@router.delete("/{id}")
async def delete_order(id: int, service: FromDishka[OrderService]):
    return await service.delete_order(id)


@router.get("/all")
async def get_all_orders(service: FromDishka[OrderService]):
    return await service.get_all_orders()


@router.get("/")
async def get_user_all_orders(
    current_user: FromDishka[UserResponse], service: FromDishka[OrderService]
):
    return await service.get_all_user_orders(current_user)


@router.get("/{id}")
async def get_order(
    id: int, 
    current_user: FromDishka[UserResponse], 
    service: FromDishka[OrderService],
):
    return await service.get_order_by_user(id, current_user)
