from fastapi import UploadFile
from starlette import status

from src.flowershop_api.core.permissions import require_roles
from src.flowershop_api.core.uow import UnitOfWork
from src.flowershop_api.models import RoleEnum
from src.flowershop_api.repositories.order import IOrderRepositories
from src.flowershop_api.schemas.order import OrderCreate, OrderResponse, OrderCreateRequest, OrderProductCreate
from src.flowershop_api.schemas.product import CreateProductRequest
from src.flowershop_api.schemas.user import UserResponse


class OrdersService:
    def __init__(self, uow: UnitOfWork, order_repository: IOrderRepositories):
        self.uow = uow
        self.orders = order_repository

    @require_roles([RoleEnum.ADMIN, RoleEnum.USER])
    async def create_order(
            self,
            user: UserResponse,
            request: OrderCreateRequest,
    ) -> OrderResponse:
        async with self.uow:
            order_data = OrderCreate(user_id=user.id, **request.model_dump())
            order = await self.orders.add(order_data)

            order_product_data = OrderProductCreate(order_id=order.id, order_product=order.order_products)
            order_products = await self.orders.add_order_products(order_product_data)

        return order_products

