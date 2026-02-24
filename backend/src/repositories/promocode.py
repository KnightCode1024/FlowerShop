from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models import Promocode, PromocodeAction
from schemas.promocode import PromoActivateCreate, PromoCreate, PromoUpdate


class IPromocodeRepository(Protocol):

    async def add(self, data: PromoCreate) -> Promocode:
        pass

    async def delete(self, id: int) -> None:
        pass

    async def update(self, data: PromoUpdate) -> Promocode:
        pass

    async def get_all(self) -> list[Promocode]:
        pass

    async def activate_user_promo(
        self,
        data: PromoActivateCreate,
    ) -> Promocode:
        pass

    async def get_promo_is_activate(
            self,
            data: PromoActivateCreate
    ) -> PromocodeAction | None:
        pass


class PromocodeRepository(IPromocodeRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: PromoCreate) -> Promocode:
        obj = Promocode(**data.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="PromocodeOrm already exists",
            )

        return obj

    async def update(self, data: PromoUpdate) -> Promocode:
        obj: Promocode | None = await self.session.get(Promocode, data.id)

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promocode not found",
            )

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(obj, field, value)

        await self.session.flush()

        return obj

    async def delete(self, id: int) -> None:
        obj: Promocode | None = await self.session.get(Promocode, id)

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promocode not found",
            )

        await self.session.delete(obj)
        await self.session.flush()

        return None

    async def get_all(self) -> list[Promocode]:
        stmt = select(Promocode)

        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result

    async def get_promo_is_activate(
        self, data: PromoActivateCreate
    ) -> PromocodeAction:
        stmt = (
            select(PromocodeAction)
            .join(Promocode, PromocodeAction.promo_id == Promocode.id)
            .where(
                Promocode.code == data.code,
                PromocodeAction.user_id == data.user_id,
            )
        )

        obj = (await self.session.execute(stmt)).scalars().one_or_none()

        if obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your already activated this promocode",
            )

        return None

    async def activate_user_promo(
            self, data: PromoActivateCreate,
            ) -> Promocode:
        stmt = (
            select(Promocode)
            .where(Promocode.code == data.code)
        )

        obj = (await self.session.execute(stmt)).scalars().one_or_none()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Promocode not found",
            )

        obj2 = PromocodeAction(promo_id=obj.id, user_id=data.user_id)

        self.session.add(obj2)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your already activated this promocode",
            )

        return obj
