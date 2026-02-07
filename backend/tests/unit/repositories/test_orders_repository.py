import pytest

from src.flowershop_api.models import User
from src.flowershop_api.schemas.order import OrderCreate, CartItem
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
    assert len(order_create_data.order_products) == len(order.order_products)
    assert order_create_data.order_products[0].product_id == order.order_products[0].product_id


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
    assert len(order_create_data.order_products) == len(order.order_products)
    assert order_create_data.order_products[0].product_id == order.order_products[0].product_id


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
    assert len(order_create_data.order_products) == len(order.order_products)
    assert order_create_data.order_products[0].product_id == order.order_products[0].product_id
