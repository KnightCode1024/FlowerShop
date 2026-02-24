import random

import pytest
from fastapi import HTTPException

from models import User
from models.order import OrderStatus
from schemas.order import CartItem, OrderCreate, OrderUpdate
from schemas.product import ProductFilterParams


@pytest.mark.asyncio
async def test_add_order_one(session, created_user, created_product, order_repository):
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(
                product_id=created_product.id,
                quantity=random.randint(1, 3),
                price=created_product.price,
            ),
        ],
    )

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id

    return order


@pytest.mark.asyncio
async def test_add_order_many(
    session, created_user: User, multiple_products, product_repository, order_repository
):
    products = await product_repository.get_filtered(filters=ProductFilterParams())
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(product_id=i.id, quantity=random.randint(1, 3), price=i.price)
            for i in products
        ],
    )

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id


@pytest.mark.asyncio
async def test_error_add_order_many_max_quantity(
    session, created_user: User, multiple_products, product_repository, order_repository
):
    products = await product_repository.get_filtered(filters=ProductFilterParams())
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(product_id=i.id, quantity=random.randint(1, 3), price=i.price)
            for i in products
        ],
    )

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id
    assert order.status == OrderStatus.IN_CART


@pytest.mark.asyncio
async def test_update_order_already_exists(
    session, created_user, created_product, product_repository, order_repository
):
    order = await test_add_order_one(
        session, created_user, created_product, order_repository
    )  # +1

    order_create_data = OrderUpdate(
        id=order.id,
        user_id=created_user.id,
        order_products=[
            CartItem(
                product_id=created_product.id,
                quantity=random.randint(1, 10),
                price=created_product.price,
            )
        ],
    )

    order_updated = await order_repository.update(order_create_data)  # +1

    assert len(order_updated.order_products) == 2
    assert order_updated.status == OrderStatus.IN_CART


@pytest.mark.asyncio
async def test_update_order_success_one(
    session,
    created_user,
    created_multiply_products,
    product_repository,
    order_repository,
):
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(
                product_id=created_multiply_products[0].id,
                quantity=random.randint(1, 3),
                price=created_multiply_products[0].price,
            )
        ],
    )

    order_added = await order_repository.add(order_create_data)

    order_update_data = OrderUpdate(
        id=order_added.id,
        user_id=created_user.id,
        order_products=[
            CartItem(
                product_id=created_multiply_products[1].id,
                quantity=random.randint(1, 10),
                price=created_multiply_products[1].price,
            )
        ],
    )

    order2_updated = await order_repository.update(order_update_data)

    assert len(order2_updated.order_products) == 2
    assert order2_updated.user_id == created_user.id
    assert order2_updated.status == OrderStatus.IN_CART


@pytest.mark.asyncio
async def test_get_all_orders_all(
    session,
    created_user,
    created_multiply_products,
    product_repository,
    order_repository,
):
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(product_id=i.id, quantity=random.randint(1, 5), price=i.price)
            for i in created_multiply_products
        ],
    )

    order_added = await order_repository.add(order_create_data)

    orders_all = await order_repository.get_all()

    assert orders_all[0].id == order_added.id
    assert len(created_multiply_products) == len(orders_all[0].order_products)


@pytest.mark.asyncio
async def test_get_all_orders_by_user(
    session,
    created_user,
    created_multiply_products,
    product_repository,
    order_repository,
):
    order_create_data = OrderCreate(
        user_id=created_user.id,
        order_products=[
            CartItem(product_id=i.id, quantity=random.randint(1, 5), price=i.price)
            for i in created_multiply_products
        ],
    )

    order_added = await order_repository.add(order_create_data)

    orders_all = await order_repository.get_all_user(created_user.id)

    assert orders_all[0].id == order_added.id
    assert order_added.user_id == created_user.id
    assert len(created_multiply_products) == len(orders_all[0].order_products)


@pytest.mark.asyncio
async def test_delete_order(
    session, created_user, created_product, product_repository, order_repository
):
    order = await test_add_order_one(
        session, created_user, created_product, order_repository
    )

    await order_repository.delete(order.id)

    with pytest.raises(HTTPException) as exp:
        await order_repository.get(order.id, created_user.id)

        assert exp.value == f"Order {order.id} not found"
