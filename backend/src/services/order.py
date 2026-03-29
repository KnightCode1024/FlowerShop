import datetime

import taskiq

from core import broker
from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from repositories.order import IOrderRepository
from schemas.order import (
    OrderCreate,
    OrderCreateRequest,
    OrderUpdate,
    OrderUpdateRequest,
)
from schemas.user import UserResponse


class OrderService:
    def __init__(self, uow: UnitOfWork, order_repository: IOrderRepository):
        self.uow = uow
        self.orders = order_repository

    @require_roles([RoleEnum.USER])
    async def create_order(self, user: UserResponse, data: OrderCreateRequest):
        order_data = OrderCreate(user_id=user.id, **data.model_dump())

        async with self.uow:
            order = await self.orders.add(order_data)

        return order

    @require_roles([RoleEnum.USER])
    async def update_order(self, user: UserResponse, data: OrderUpdateRequest):
        order_data = OrderUpdate(
            id=data.order_id,
            user_id=user.id,
            **data.model_dump(
                exclude_none=True,
            )
        )

        async with self.uow:
            order = await self.orders.update(order_data)

        return order

    @require_roles([RoleEnum.USER])
    async def get_all_user_orders(self, user: UserResponse):
        async with self.uow:
            orders = await self.orders.get_all_user(user.id)
        return orders

    @require_roles([RoleEnum.USER])
    async def get_user_purchases(self, user: UserResponse):
        async with self.uow:
            orders = await self.orders.get_purchases_user(user.id)
        return [order.to_entity() for order in orders]

    @require_roles([RoleEnum.USER])
    async def get_order_by_user(self, id: int, user: UserResponse):
        async with self.uow:
            order = await self.orders.get(id, user.id)
            return order

    @require_roles([RoleEnum.USER])
    async def get_cart(self, user: UserResponse):
        async with self.uow:
            order = await self.orders.get_cart(user.id)
            if order:
                return order

            order = await self.orders.add(
                OrderCreate(user_id=user.id, order_products=[])
            )
            return order

    @require_roles([RoleEnum.USER])
    async def update_cart(self, user: UserResponse, data: OrderCreateRequest):
        async with self.uow:
            order = await self.orders.get_cart(user.id)
            if order:
                return await self.orders.update(
                    OrderUpdate(
                        id=order.id,
                        user_id=user.id,
                        order_products=data.order_products,
                    )
                )

            return await self.orders.add(
                OrderCreate(
                    user_id=user.id,
                    order_products=data.order_products,
                )
            )

    @require_roles([RoleEnum.ADMIN])
    async def delete_order(self, id: int, user: UserResponse):
        async with self.uow:
            await self.orders.delete(id)

    @require_roles([RoleEnum.ADMIN])
    async def get_all_orders(self, user: UserResponse):
        async with self.uow:
            orders = await self.orders.get_all()
        return orders

    @broker.task("orders-analytics")
    @require_roles([RoleEnum.ADMIN])
    async def get_analytics(self, user: UserResponse):
        async with self.uow:
            orders_analytics = await self.orders.get_analytics_orders()

        return orders_analytics
