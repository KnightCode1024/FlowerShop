from fastapi import UploadFile
from starlette import status

from src.flowershop_api.core.permissions import require_roles
from src.flowershop_api.core.uow import UnitOfWork
from src.flowershop_api.models import RoleEnum
from src.flowershop_api.repositories.order import IOrderRepositories
from src.flowershop_api.schemas.order import OrderCreate, OrderResponse, OrderCreateRequest, OrderProductCreate, OrderUpdateRequest, OrderUpdate
from src.flowershop_api.schemas.product import CreateProductRequest
from src.flowershop_api.schemas.user import UserResponse


class OrdersService:
    def __init__(self, uow: UnitOfWork, order_repository: IOrderRepositories):
        self.uow = uow
        self.orders = order_repository

    @require_roles([RoleEnum.ADMIN, RoleEnum.USER])
    async def create_order(self, user: UserResponse, data: OrderCreateRequest):
        order_data = OrderCreate(user_id=user.id, **data.model_dump())

        async with self.uow:
            order = await self.orders.add(order_data)

        return order


    @require_roles([RoleEnum.ADMIN, RoleEnum.USER])
    async def update_order(self, user: UserResponse, data: OrderUpdateRequest):
        order_data = OrderUpdate(id=data.order_id,
                                 user_id=user.id,
                                 **data.model_dump(exclude_none=True))

        async with self.uow:
            order = await self.orders.update(order_data)

        return order


    @require_roles([RoleEnum.ADMIN, RoleEnum.USER])
    async def delete_order(self, id: int, user: UserResponse, data: OrderUpdateRequest):
        async with self.uow:
            return await self.orders.delete(id)

