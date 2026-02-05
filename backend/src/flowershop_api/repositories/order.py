from typing import Protocol

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.flowershop_api.schemas.order import OrderCreate, Order, OrderUpdate


class IOrderRepositories(Protocol):
    async def add(self, order_data: OrderCreate) -> Order:
        pass

    async def update(self, order_data: OrderUpdate) -> Order:
        pass

    async def get_all(self) -> list[Order]:
        pass

    async def get(self) -> Order:
        pass

    async def delete(self) -> None:
        pass

    async def get_by_filters(self) -> list[Order]:
        pass


class OrderRepositories(IOrderRepositories):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order_data: OrderCreate) -> Order:
        obj = Order(**order_data.model_dump())

        try:
            await self.session.flush()
        except IntegrityError:
            raise

        await self.session.refresh(obj)
        return obj
