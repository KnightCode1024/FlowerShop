import pytest
from fastapi import HTTPException

from models import User
from repositories import PromocodeRepository, UserRepository
from schemas.promocode import PromoCreateRequest, PromoCreate, PromoUpdate, PromoActivateCreate


@pytest.mark.asyncio
async def test_promocode_create(promocodes_repository: PromocodeRepository):
    promocode_data = PromoCreate(code="NEWYEAR",
                                 max_count_activators=102,
                                 percent=12.5)
    promocode = await promocodes_repository.add(promocode_data)

    assert promocode.code == promocode_data.code
    assert promocode_data.percent == promocode.percent


@pytest.mark.asyncio
async def test_promocode_create_without_code(promocodes_repository: PromocodeRepository):
    promocode_data = PromoCreate(max_count_activators=102,
                                 percent=12.5)
    promocode = await promocodes_repository.add(promocode_data)

    assert promocode_data.percent == promocode.percent
    assert promocode_data.max_count_activators == promocode.max_count_activators


@pytest.mark.asyncio
async def test_promocode_update(promocodes_repository: PromocodeRepository):
    promocode_data = PromoCreate(max_count_activators=102,
                                 percent=12.5)
    promocode = await promocodes_repository.add(promocode_data)

    promocode_data_update = PromoUpdate(
        id=promocode.id,
        max_count_activators=1,
        percent=80,
        code=promocode.code
    )
    promocode_updated = await promocodes_repository.update(promocode_data_update)

    assert promocode_updated.percent == promocode_data_update.percent
    assert promocode_updated.max_count_activators == promocode_data_update.max_count_activators


@pytest.mark.asyncio
async def test_promocode_delete(promocodes_repository: PromocodeRepository):
    promocode_data = PromoCreate(max_count_activators=102,
                                 percent=12.5)
    promocode = await promocodes_repository.add(promocode_data)

    await promocodes_repository.delete(promocode.id)

    get_promos = await promocodes_repository.get_all()

    assert get_promos == []


@pytest.mark.asyncio
async def test_promocode_get_all(promocodes_repository: PromocodeRepository):
    promocode_data = PromoCreate(max_count_activators=102,
                                 percent=12.5)
    for i in range(10):
        await promocodes_repository.add(promocode_data)

    get_promos = await promocodes_repository.get_all()

    assert len(get_promos) == 10


@pytest.mark.asyncio
async def test_promocode_activate(promocodes_repository: PromocodeRepository, created_user: User):
    promocode_data = PromoCreate(max_count_activators=102,
                                 percent=50)
    promo = await promocodes_repository.add(promocode_data)

    promo_activate = PromoActivateCreate(
        user_id=created_user.id,
        code=promo.code
    )
    promo_activated = await promocodes_repository.activate_user_promo(promo_activate)

    assert promo_activated.promo_id == promo.id
    assert promo_activated.user_id == created_user.id

    with pytest.raises(HTTPException) as exp:
        promo_activated2 = await promocodes_repository.activate_user_promo(promo_activate)
        assert exp.value == "Your already activated this promocode"

