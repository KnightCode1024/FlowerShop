from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from schemas.promocode import (PromoActivateRequest, PromoCreateRequest,
                               PromoUpdateRequest)
from schemas.user import UserResponse
from services.promocode import PromocodeService

<<<<<<< HEAD
router = APIRouter(
    prefix="/promocodes",
    tags=["Promocodes"],
    route_class=DishkaRoute,
)
=======
router = APIRouter(prefix="/promocodes", tags=["Promocode"], route_class=DishkaRoute)
>>>>>>> origin/main


@router.get("/")
async def get_promos(service: FromDishka[PromocodeService]):
    return await service.get_promos()


@router.post("/activate")
async def activate_promo(
    promo: PromoActivateRequest,
    current_user: FromDishka[UserResponse],
    service: FromDishka[PromocodeService],
):
    return await service.activate_promo(promo, current_user.id)


@router.post("/")
async def create_promo(data: PromoCreateRequest, service: FromDishka[PromocodeService]):
    return await service.create_promo(data)


@router.delete("/{id}")
async def delete_promo(id: int, service: FromDishka[PromocodeService]):
    return await service.delete_promo(id)


@router.patch("/{id}")
async def update_promo(
    id: int, data: PromoUpdateRequest, service: FromDishka[PromocodeService]
):
    return await service.update_promo(id, data)
