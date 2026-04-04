from core.exceptions import PromocodeNotFoundError
from core.permissions import require_roles
from core.uow import UnitOfWork
from fastapi import HTTPException
from models import RoleEnum
from repositories.promocode import IPromocodeRepository
from schemas.promocode import (PromoCreate, PromoCreateRequest, PromoUpdate,
                               PromoUpdateRequest)
from starlette import status


class PromocodeService:
    def __init__(self, uow: UnitOfWork, promocode_repository: IPromocodeRepository):
        self.uow = uow
        self.repository = promocode_repository

    @require_roles([RoleEnum.ADMIN, RoleEnum.EMPLOYEE])
    async def create_promo(self, user, data: PromoCreateRequest):
        promo_data = PromoCreate(**data.model_dump())
        # try:
        async with self.uow:
            promo = await self.repository.add(promo_data)
        return promo
        # except ValueError as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT,
        #         detail=str(e),
        #     )

    @require_roles([RoleEnum.ADMIN, RoleEnum.ADMIN])
    async def delete_promo(self, user, id: int):
        try:
            async with self.uow:
                await self.repository.delete(id)
        except PromocodeNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    @require_roles([RoleEnum.EMPLOYEE, RoleEnum.ADMIN])
    async def update_promo(self, user, id: int, data: PromoUpdateRequest):
        promo_data = PromoUpdate(id=id, **data.model_dump())
        try:
            async with self.uow:
                updated_promo = await self.repository.update(promo_data)
            return updated_promo
        except PromocodeNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    @require_roles([RoleEnum.ADMIN, RoleEnum.EMPLOYEE])
    async def get_promos(self, user):
        async with self.uow:
            return await self.repository.get_all()
