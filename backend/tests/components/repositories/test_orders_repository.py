import random

import pytest
from fastapi import HTTPException

from src.flowershop_api.models import User
from src.flowershop_api.schemas.order import OrderCreate, CartItem, OrderUpdate
from src.flowershop_api.schemas.product import ProductFilterParams


# pytest -v test_orders_repository.py

@pytest.mark.asyncio
async def test_add_order_one(session, created_user, created_product, order_repository):
    order_create_data = OrderCreate(user_id=created_user.id, order_products=[
        CartItem(
            product_id=created_product.id,
            quantity=3,
            price=created_product.price
        ),
    ])

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id

    return order


@pytest.mark.asyncio
async def test_add_order_many(session, created_user: User, multiple_products, product_repository, order_repository):
    products = await product_repository.get_filtered(filters=ProductFilterParams())
    order_create_data = OrderCreate(user_id=created_user.id, order_products=[
        CartItem(
            product_id=i.id,
            quantity=i.quantity,
            price=i.price
        ) for i in products
    ])

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id


@pytest.mark.asyncio
async def test_error_add_order_many_max_quantity(session, created_user: User, multiple_products, product_repository, order_repository):
    products = await product_repository.get_filtered(filters=ProductFilterParams())
    order_create_data = OrderCreate(user_id=created_user.id, order_products=[
        CartItem(
            product_id=i.id,
            quantity=i.quantity + 1,
            price=i.price
        ) for i in products
    ])

    order = await order_repository.add(order_create_data)

    assert order.user_id == created_user.id


@pytest.mark.asyncio
async def test_update_order_already_exists(session, created_user, created_product, product_repository, order_repository):
    order = await test_add_order_one(session, created_user, created_product, order_repository)

    order_create_data = OrderUpdate(id=order.id, user_id=created_user.id, order_products=[
        CartItem(
            product_id=created_product.id,
            quantity=random.randint(1, 10),
            price=created_product.price
        )
    ])

    with pytest.raises(HTTPException) as exp:
        order = await order_repository.add(order_create_data)
        assert exp.value == "Product in order 1 already exists"


@pytest.mark.asyncio
async def test_update_order_success_one(session, created_user, created_multiply_products, product_repository, order_repository):
    order_create_data = OrderCreate(user_id=created_user.id, order_products=[
        CartItem(
            product_id=created_multiply_products[0].id,
            quantity=created_multiply_products[0].quantity + 1,
            price=created_multiply_products[0].price
        )
    ])

    order_added = await order_repository.add(order_create_data)

    print(order_added, order_added.order_products)

    order_update_data = OrderUpdate(id=order_added.id, user_id=created_user.id, order_products=[
        CartItem(
            product_id=created_multiply_products[1].id,
            quantity=random.randint(1, 10),
            price=created_multiply_products[1].price
        )
    ])

    order2_updated = await order_repository.update(order_update_data)

    print(order2_updated)

    print(order2_updated.order_products)

    assert len(order2_updated.order_products) == 2
    assert order2_updated.user_id == created_user.id
