from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.promocode import Promocodes, PromocodeActions
from schemas.promocode import PromoUpdate, PromoCreate, PromoActivateCreate


class IPromocodeRepository(Protocol):

    async def add(self, data: PromoCreate) -> Promocodes:
        pass

    async def delete(self, id: int) -> None:
        pass

    async def update(self, data: PromoUpdate) -> Promocodes:
        pass

    async def get_all(self) -> list[Promocodes]:
        pass

    async def activate_user_promo(self, data: PromoActivateCreate) -> PromocodeActions:
        pass

    async def get_promo_is_activate(self, data: PromoActivateCreate) -> PromocodeActions | None:
        pass


class PromocodeRepository(IPromocodeRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: PromoCreate) -> Promocodes:
        obj = Promocodes(**data.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="PromocodeOrm already exists"
            )

        return obj

    async def update(self, data: PromoUpdate) -> Promocodes:
        obj: Promocodes | None = await self.session.get(Promocodes, data.id)

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocode not found")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(obj, field, value)

        await self.session.flush()

        return obj

    async def delete(self, id: int) -> None:
        obj: Promocodes | None = await self.session.get(Promocodes, id)

        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocode not found")

        await self.session.delete(obj)
        await self.session.flush()

        return None

    async def get_all(self) -> list[Promocodes]:
        stmt = select(Promocodes)

        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result

    async def get_promo_is_activate(self, data: PromoActivateCreate) -> PromocodeActions:
        stmt = (
            select(PromocodeActions)
            .join(
                Promocodes, PromocodeActions.promo_id == Promocodes.id
            )
            .where(Promocodes.code == data.code,
                   PromocodeActions.user_id == data.user_id)
        )

        obj = (await self.session.execute(stmt)).scalars().one_or_none()

        if obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your already activated this promocode"
            )

        return None

    async def activate_user_promo(self, data: PromoActivateCreate) -> PromocodeActions:
        stmt = (
            select(Promocodes)
            .where(Promocodes.code == data.code)
        )

        obj = (await self.session.execute(stmt)).scalars().one_or_none()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Promocode not found"
            )

        obj = PromocodeActions(promo_id=obj.id, **data.model_dump())

        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your already activated this promocode"
            )

        return obj
