import pytest

from src.flowershop_api.repositories.product_image import ProductImageRepository


@pytest.mark.asyncio
async def test_create_and_get_by_id(session, created_product):
    repo = ProductImageRepository(session=session)

    created = await repo.create_for_product(
        product_id=created_product.id, url="http://example/1.png", order=0, is_primary=True
    )
    await session.flush()

    assert created.id is not None
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.url == "http://example/1.png"
    assert fetched.is_primary is True


@pytest.mark.asyncio
async def test_get_by_product_id_returns_ordered(session, created_product):
    repo = ProductImageRepository(session=session)

    await repo.create_for_product(created_product.id, url="u1.png", order=2)
    await repo.create_for_product(created_product.id, url="u2.png", order=1)
    await repo.create_for_product(created_product.id, url="u3.png", order=3)
    await session.flush()

    images = await repo.get_by_product_id(created_product.id)
    assert len(images) == 3
    orders = [img.order for img in images]
    assert orders == sorted(orders)


@pytest.mark.asyncio
async def test_update_success_and_non_existing(session, created_product):
    repo = ProductImageRepository(session=session)

    created = await repo.create_for_product(created_product.id, url="old.png", order=0)
    await session.flush()

    updated = await repo.update(created.id, {"url": "new.png", "is_primary": True})
    assert updated is not None
    assert updated.url == "new.png"
    assert updated.is_primary is True

    not_found = await repo.update(99999, {"url": "x"})
    assert not_found is None


@pytest.mark.asyncio
async def test_delete_and_delete_non_existing(session, created_product):
    repo = ProductImageRepository(session=session)

    created = await repo.create_for_product(created_product.id, url="todelete.png", order=0)
    await session.flush()

    res = await repo.delete(created.id)
    assert res is True

    res2 = await repo.delete(999999)
    assert res2 is False


@pytest.mark.asyncio
async def test_delete_by_product_id_returns_rowcount(session, created_product):
    repo = ProductImageRepository(session=session)

    await repo.create_for_product(created_product.id, url="a.png", order=0)
    await repo.create_for_product(created_product.id, url="b.png", order=1)
    await session.flush()

    count = await repo.delete_by_product_id(created_product.id)
    # should delete two records
    assert count >= 2
