from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import select, desc, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.flowershop_api.models.order import Order, OrderProduct
from src.flowershop_api.schemas.order import OrderCreate, OrderUpdate, CartItem, OrderProductCreate
from starlette import status


class IOrderRepositories(Protocol):
    async def add(self, order_data: OrderCreate) -> Order:
        pass

    async def add_order_products(self, order_data: OrderProductCreate) -> Order:
        pass

    async def update(self, order_data: OrderUpdate) -> Order:
        pass

    async def get_all(self) -> list[Order]:
        pass

    async def get(self, id: int) -> Order:
        pass

    async def delete(self, id: int) -> None:
        pass

    async def get_by_filters(self, filters) -> list[Order]:
        pass


class OrderRepositories(IOrderRepositories):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order_data: OrderCreate) -> Order:
        obj: Order = Order(**order_data.model_dump(exclude={"order_products"}))
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Order already exists"
            )

        return obj

    async def add_order_products(self, order_data: OrderProductCreate):
        obj = OrderProduct(order_id=order_data.order_id,
                           **order_data.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exists product in order")

        stmt_order = (
            select(Order).where(Order.id == order_data.order_id)
            .outerjoin(OrderProduct, OrderProduct.order_id == order_data.order_id)
        )

        result = await self.session.execute(stmt_order)
        result = result.scalar_one_or_none()

        return result

    async def get(self, id: int) -> Order:
        obj: Order | None = await self.session.get(Order, id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return obj

    async def update(self, order_data: OrderUpdate) -> Order:
        obj = await self.get(order_data.id)

        for name, value in order_data.model_dump(exclude_none=True).items():
            setattr(obj, name, value)

        await self.session.flush()
        return obj

    async def get_all(self) -> list[Order]:
        stmt = select(Order).order_by(
            Order.created_at.desc(),
        )
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result

    async def delete(self, id: int) -> None:
        order = await self.get(id)
        await self.session.delete(order)
        await self.session.flush()
        return None
