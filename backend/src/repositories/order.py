import datetime
import time
from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import desc, insert, outerjoin, select, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from models.order import Order, OrderProduct
from schemas.order import (CartItem, OrderCreate, OrderProductCreate,
                           OrderUpdate, OrdersAnalytics)


class IOrderRepository(Protocol):
    async def add(self, order_data: OrderCreate) -> Order:
        pass

    async def update(self, order_data: OrderUpdate) -> Order:
        pass

    async def get_all(self) -> list[Order]:
        pass

    async def get_all_user(self, user_id: int) -> list[Order]:
        pass

    async def get_analytics_orders(self) -> OrdersAnalytics:
        pass

    async def get(self, id: int, user_id: int) -> Order:
        pass

    async def delete(self, id: int) -> None:
        pass


class OrderRepository(IOrderRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order_data: OrderCreate) -> Order:
        obj: Order = Order(**order_data.model_dump(exclude={"order_products"}))
        self.session.add(obj)

        await self.session.flush()
        await self._update_products(obj, order_data.order_products)

        stmt = (
            select(Order)
            .options(joinedload(Order.order_products))
            .where(Order.id == obj.id)
        )

        result = await self.session.execute(stmt)
        result = result.scalars().unique().one_or_none()

        return result

    async def get(self, id: int, user_id: int = None) -> Order:
        stmt = (
            select(Order)
            .options(joinedload(Order.order_products))
            .where(Order.id == id)
        )

        if user_id:
            stmt.where(Order.user_id == user_id)

        result = await self.session.execute(stmt)
        obj: Order | None = result.scalars().unique().one_or_none()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {id} not found"
            )

        return obj

    async def update(self, order_data: OrderUpdate) -> Order:
        obj = await self.get(order_data.id, order_data.user_id)

        if order_data.order_products:
            await self._update_products(obj, order_data.order_products)

        for name, value in order_data.model_dump(
                exclude_none=True, exclude={"order_products"}
        ).items():
            setattr(obj, name, value)

        stmt = (
            select(Order)
            .options(joinedload(Order.order_products))
            .where(Order.id == obj.id)
        )

        result = await self.session.execute(stmt)
        result = result.scalars().unique().one_or_none()

        return result

    async def get_all(self) -> list[Order]:
        stmt = (
            select(Order)
            .order_by(
                Order.created_at.desc(),
            )
            .options(joinedload(Order.order_products))
        )
        result = await self.session.execute(stmt)
        result = result.scalars().unique().all()
        return result

    async def get_all_user(self, user_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .order_by(
                Order.created_at.desc(),
            )
            .where(Order.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        result = result.scalars().unique().all()
        return result

    async def get_analytics_orders(self) -> OrdersAnalytics:
        today = datetime.datetime.today()
        day_1 = datetime.datetime.combine(today - datetime.timedelta(days=1), datetime.time.min)
        day_7 = datetime.datetime.combine(today - datetime.timedelta(days=7), datetime.time.min)
        day_30 = datetime.datetime.combine(today - datetime.timedelta(days=30), datetime.time.min)

        stmt = (
            select(
                func.count(Order.id).label("count_orders"),

                func.count(Order.id).filter(Order.created_at >= day_1).label("count_1_days_orders"),
                func.count(Order.id).filter(Order.created_at >= day_7).label("count_7_days_orders"),
                func.count(Order.id).filter(Order.created_at >= day_30).label("count_30_days_orders"),

                func.sum(Order.amount).label("amount_for_all_orders"),

                func.sum(Order.amount).filter(Order.created_at >= day_1).label("amount_for_1_days_orders"),
                func.sum(Order.amount).filter(Order.created_at >= day_7).label("amount_for_7_days_orders"),
                func.sum(Order.amount).filter(Order.created_at >= day_30).label("amount_for_30_days_orders"),

            )
        )
        result1 = await self.session.execute(stmt)
        result1 = result1.mappings().one()

        return OrdersAnalytics(**result1)

    async def delete(self, id: int) -> None:
        order = await self.get(id)
        await self.session.delete(order)
        await self.session.flush()
        return None

    async def _update_products(
            self, order: Order, order_products: list[CartItem]
    ) -> Order:
        new_order_products = []

        for o_prod in order_products:
            op = OrderProduct(
                order_id=order.id,
                product_id=o_prod.product_id,
                quantity=o_prod.quantity,
                price=o_prod.price,
            )
            new_order_products.append(op)

        self.session.add_all(new_order_products)

        order.amount = round(
            float(sum([i.quantity * i.price for i in order_products])), 2
        )

        await self.session.flush()
        await self.session.refresh(order)

        return order
