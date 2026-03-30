import datetime

import taskiq

from core import broker
from core.exceptions import (OrderInvalidStatusError, OrderNotFoundError,
                             ProductInsufficientStockError)
from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from models.order import OrderProduct, OrderStatus
from repositories.order import IOrderRepository
from repositories.product import IProductRepository
from schemas.order import (
    OrderCreate,
    OrderCreateRequest,
    OrderUpdate,
    OrderUpdateRequest,
)
from schemas.product import ProductUpdate
from schemas.user import UserResponse


class OrderService:
    def __init__(
        self,
        uow: UnitOfWork,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
    ):
        self.uow = uow
        self.orders = order_repository
        self.products = product_repository

    async def _validate_and_prepare_order_products(
        self,
        order_items: list,
    ) -> list[OrderProduct]:
        """Validate order items and return OrderProduct objects."""
        if not order_items:
            return []

        aggregated: dict[int, int] = {}
        for item in order_items:
            if item.quantity <= 0:
                raise ValueError("Quantity must be greater than zero")
            aggregated[item.product_id] = aggregated.get(item.product_id, 0) + item.quantity

        products = await self.products.get_products_by_ids(list(aggregated.keys()))

        if len(products) != len(aggregated):
            found_ids = {p.id for p in products}
            missing_ids = set(aggregated.keys()) - found_ids
            raise ValueError(f"Products not found: {missing_ids}")

        order_products = []
        for product in products:
            quantity = aggregated[product.id]
            if product.quantity < quantity:
                raise ProductInsufficientStockError(
                    product.id, product.quantity, quantity
                )
            price = float(product.price)
            order_products.append(
                OrderProduct(
                    order_id=None,
                    product_id=product.id,
                    quantity=quantity,
                    price=price,
                )
            )

        return order_products

    async def deduct_product_quantities(self, order_id: int) -> None:
        """
        Business logic: Deduct product quantities after successful payment.
        """
        async with self.uow:
            order = await self.orders.get(order_id, user_id=None)

            if not order:
                raise OrderNotFoundError(order_id)

            if not order.order_products:
                return

            for order_product in order.order_products:
                product = await self.products.get_by_id(order_product.product_id)
                if product:
                    new_quantity = product.quantity - order_product.quantity
                    new_in_stock = new_quantity > 0
                    await self.products.update(
                        order_product.product_id,
                        ProductUpdate(
                            quantity=new_quantity,
                            in_stock=new_in_stock,
                        ),
                    )

    async def restore_product_quantities(self, order_id: int) -> None:
        """
        Business logic: Restore product quantities when order is cancelled/expired.
        """
        async with self.uow:
            order = await self.orders.get(order_id, user_id=None)

            if not order:
                raise OrderNotFoundError(order_id)

            if not order.order_products:
                return

            for order_product in order.order_products:
                product = await self.products.get_by_id(order_product.product_id)
                if product:
                    new_quantity = product.quantity + order_product.quantity
                    new_in_stock = new_quantity > 0
                    await self.products.update(
                        order_product.product_id,
                        ProductUpdate(
                            quantity=new_quantity,
                            in_stock=new_in_stock,
                        ),
                    )

    @require_roles([RoleEnum.USER])
    async def create_order(self, user: UserResponse, data: OrderCreateRequest):
        order_data = OrderCreate(
            user_id=user.id,
            order_products=data.order_products,
            **(data.delivery_address.model_dump() if data.delivery_address else {}),
        )

        async with self.uow:
            order = await self.orders.add(order_data)

        return order

    @require_roles([RoleEnum.USER])
    async def update_order(self, user: UserResponse, data: OrderUpdateRequest):
        update_dict = {
            "id": data.order_id,
            "user_id": user.id,
            "order_products": data.order_products,
        }
        if data.delivery_address:
            update_dict.update(data.delivery_address.model_dump())

        order_data = OrderUpdate(**update_dict)

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
            if not order:
                raise OrderNotFoundError(id)
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
                update_dict = {
                    "id": order.id,
                    "user_id": user.id,
                    "order_products": data.order_products,
                }
                if data.delivery_address:
                    update_dict.update(data.delivery_address.model_dump())
                return await self.orders.update(OrderUpdate(**update_dict))

            return await self.orders.add(
                OrderCreate(
                    user_id=user.id,
                    order_products=data.order_products,
                    **(data.delivery_address.model_dump() if data.delivery_address else {}),
                )
            )

    @require_roles([RoleEnum.ADMIN])
    async def delete_order(self, id: int, user: UserResponse):
        order = await self.orders.get(id)
        if not order:
            raise OrderNotFoundError(id)

        async with self.uow:
            await self.restore_product_quantities(id)
            await self.orders.delete(id)

    @require_roles([RoleEnum.ADMIN])
    async def cancel_order(self, id: int, user: UserResponse):
        """Cancel order and restore product quantities."""
        order = await self.orders.get(id)
        if not order:
            raise OrderNotFoundError(id)

        async with self.uow:
            await self.restore_product_quantities(id)
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
