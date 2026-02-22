from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from repositories.promocode import IPromocodeRepository
from schemas.promocode import (
    PromoCreateRequest,
    PromoCreate,
    PromoUpdateRequest,
    PromoActivateCreate,
    PromoActivateRequest,
    PromoUpdate,
)


class PromocodeService:
    def __init__(self, uow: UnitOfWork, promocode_repository: IPromocodeRepository):
        self.uow = uow
        self.repository = promocode_repository

    @require_roles([RoleEnum.ADMIN, RoleEnum.EMPLOYEE])
    async def create_promo(self, data: PromoCreateRequest):
        promo_data = PromoCreate(**data.model_dump())

        async with self.uow:
            return await self.repository.add(promo_data)

    @require_roles([RoleEnum.USER])
    async def activate_promo(self, promo_code_data: PromoActivateRequest, user_id: int):
        promo_data = PromoActivateCreate(
            user_id=user_id, **promo_code_data.model_dump()
        )

        async with self.uow:
            promo_operation = await self.repository.activate_user_promo(promo_data)
            return promo_operation

    @require_roles([RoleEnum.ADMIN, RoleEnum.ADMIN])
    async def delete_promo(self, id: int):
        async with self.uow:
            await self.repository.delete(id)

    @require_roles([RoleEnum.EMPLOYEE, RoleEnum.ADMIN])
    async def update_promo(self, id: int, data: PromoUpdateRequest):
        promo_data = PromoUpdate(id=id, **data.model_dump())
        async with self.uow:
            updated_promo = await self.repository.update(promo_data)

        return updated_promo

    @require_roles([RoleEnum.ADMIN, RoleEnum.EMPLOYEE])
    async def get_promos(self):
        async with self.uow:
            return await self.repository.get_all()
