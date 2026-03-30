import datetime
import time
from typing import Protocol

from sqlalchemy import desc, insert, outerjoin, select, update, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from models import PromocodeAction, Promocode
from models.order import Order, OrderProduct
from models.product import Product
from schemas.order import (CartItem, OrderCreate, OrderProductCreate,
                           OrderUpdate, OrdersAnalytics)
from schemas.order import OrderStatus
from utils.numbers import get_percent


class IOrderRepository(Protocol):
    async def add(self, order_data: OrderCreate) -> Order:
        pass

    async def update(self, order_data: OrderUpdate) -> Order:
        pass

    async def get_all(self) -> list[Order]:
        pass

    async def get_all_user(self, user_id: int) -> list[Order]:
        pass

    async def get_purchases_user(self, user_id: int) -> list[Order]:
        pass

    async def get_cart(self, user_id: int) -> Order | None:
        pass

    async def get_analytics_orders(self) -> OrdersAnalytics:
        pass

    async def get(self, id: int, user_id: int) -> Order:
        pass

    async def delete(self, id: int) -> None:
        pass

    async def get_order_products(self, order_id: int) -> list[OrderProduct]:
        pass

    async def clear_order_products(self, order_id: int) -> None:
        pass

    async def add_order_products(self, order_id: int, order_products: list[OrderProduct]) -> None:
        pass

    async def get_products_for_order(self, product_ids: list[int]) -> list[Product]:
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
            stmt = stmt.where(Order.user_id == user_id)

        result = await self.session.execute(stmt)
        obj: Order | None = result.scalars().unique().one_or_none()

        return obj

    async def update(self, order_data: OrderUpdate) -> Order:
        obj = await self.get(order_data.id, order_data.user_id)

        if order_data.promocode:
            await self.check_promo(obj, order_data)

        if order_data.order_products is not None:
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

    async def check_promo(self, obj: Order, order_data: OrderUpdate):
        stmt = (
            select(Promocode)
            .where(Promocode.code == order_data.promocode)
        )

        promo_obj = (await self.session.execute(stmt)).scalars().one_or_none()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Promocode not found",
            )

        obj2 = PromocodeAction(promo_id=obj.id, user_id=order_data.user_id)

        self.session.add(obj2)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your already activated this promocode",
            )

        order_data.amount = get_percent(order_data.amount, promo_obj.percent)

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
            .options(joinedload(Order.order_products))
        )
        result = await self.session.execute(stmt)
        result = result.scalars().unique().all()
        return result

    async def get_purchases_user(self, user_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .order_by(Order.created_at.desc())
            .where(Order.user_id == user_id, Order.status != OrderStatus.IN_CART)
            .options(joinedload(Order.order_products))
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_cart(self, user_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id, Order.status == OrderStatus.IN_CART)
            .order_by(Order.created_at.desc())
            .options(joinedload(Order.order_products))
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().first()

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

    async def get_order_products(self, order_id: int) -> list[OrderProduct]:
        stmt = select(OrderProduct).where(OrderProduct.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def clear_order_products(self, order_id: int) -> None:
        await self.session.execute(
            delete(OrderProduct).where(OrderProduct.order_id == order_id)
        )
        await self.session.flush()

    async def add_order_products(self, order_id: int, order_products: list[OrderProduct]) -> None:
        self.session.add_all(order_products)
        await self.session.flush()

    async def get_products_for_order(self, product_ids: list[int]) -> list[Product]:
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _update_products(
            self, order: Order, order_products: list[CartItem]
    ) -> Order:
        await self.clear_order_products(order.id)

        if not order_products:
            order.amount = 0.00
            await self.session.flush()
            await self.session.refresh(order)
            return order

        product_ids = [item.product_id for item in order_products]
        products = await self.get_products_for_order(product_ids)

        new_order_products = []
        total_amount = 0.0

        for product in products:
            quantity = sum(item.quantity for item in order_products if item.product_id == product.id)
            price = float(product.price)
            total_amount += quantity * price
            new_order_products.append(
                OrderProduct(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price,
                )
            )

        await self.add_order_products(order.id, new_order_products)

        order.amount = round(float(total_amount), 2)

        await self.session.flush()
        await self.session.refresh(order)

        return order
