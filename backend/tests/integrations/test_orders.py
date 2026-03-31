import random
from http.client import HTTPException

import pytest
from httpx import AsyncClient

from schemas.order import CartItem, OrderCreateRequest, OrderResponse, OrderUpdateRequest
from schemas.promocode import PromoCreate, PromoCreateRequest, PromocodeResponse
from utils.numbers import get_percent


@pytest.mark.asyncio
async def test_success_order_update_with_promocode(created_user_client: AsyncClient, created_admin_client: AsyncClient, created_product):
    promocode_data = PromoCreateRequest(code="NEWYEAR",
                                        max_count_activators=102,
                                        percent=10)
    response1 = await created_admin_client.post("/promocodes/", json=promocode_data.model_dump())
    promocode = PromocodeResponse(**response1.json())

    assert promocode.code == promocode_data.code
    assert promocode_data.percent == promocode.percent

    orders_data = OrderCreateRequest(order_products=[
        CartItem(product_id=created_product.id,
                 quantity=1,
                 price=created_product.price) for i in range(5)

    ])
    response2 = await created_user_client.post("/orders/", json=orders_data.model_dump())
    order = OrderResponse(**response2.json())

    order_update_data = OrderUpdateRequest(
        id=order.id,
        promocode=promocode.code
    )

    response3 = await created_user_client.patch(f"/orders/", json=order_update_data.model_dump())
    updated_order = OrderResponse(**response3.json())

    assert updated_order.amount == get_percent(order.amount, promocode.percent), f"old amount - not activate promocode {promocode.percent}%"

    return updated_order, promocode


@pytest.mark.asyncio
async def test_failed_order_already_activated_promo(created_user_client: AsyncClient, created_admin_client: AsyncClient, created_product):
    order, promo = await test_success_order_update_with_promocode(created_user_client, created_admin_client, created_product)

    order_update_data = OrderUpdateRequest(
        id=order.id,
        promocode=promo.code
    )

    response = await created_user_client.patch(f"/orders/", json=order_update_data.model_dump())

    assert response.status_code == 409
    assert response.json()["detail"] == "Promocode already activated"


# @pytest.mark.asyncio
# async def test_failed_order_max_count_act_promo(created_user_client: AsyncClient, created_admin_client: AsyncClient, created_product, created_users):
#     user1_cl, user2_cl, user3_cl = created_users
#
#     promocode_data = PromoCreateRequest(code=f"NEWYEAR{random.randint(2000, 2040)}",
#                                         max_count_activators=2,
#                                         percent=10)
#
#     response1 = await created_admin_client.post("/promocodes/", json=promocode_data.model_dump())
#     promocode = PromocodeResponse(**response1.json())
#
#     assert promocode.code == promocode_data.code
#     assert promocode_data.percent == promocode.percent
#
#     orders_data = OrderCreateRequest(order_products=[
#         CartItem(product_id=created_product.id,
#                  quantity=1,
#                  price=created_product.price) for i in range(5)
#
#     ])
#     response2 = await created_user_client.post("/orders/", json=orders_data.model_dump())
#     order = OrderResponse(**response2.json())
#
#     order_update_data = OrderUpdateRequest(
#         id=order.id,
#         promocode=promocode.code
#     )
#
#     response3 = await created_user_client.patch(f"/orders/", json=order_update_data.model_dump())  # activate promocode with order
#     updated_order1 = OrderResponse(**response3.json())
#
#     assert order.id == updated_order1.id
#     assert updated_order1.amount == get_percent(order.amount, promocode.percent), f"old amount - not activate promocode {promocode.percent}%"
#
#     response4 = await user2_cl.patch(f"/orders/", json=order_update_data.model_dump())
#     updated_order2 = OrderResponse(**response4.json())
#
#     assert updated_order2.amount == get_percent(order.amount, promocode.percent), f"old amount - not activate promocode {promocode.percent}%"
#
#     response5 = await user3_cl.patch(f"/orders/", json=order_update_data.model_dump())
#
#     assert response5.status_code == 403
#     assert response5.json()["detail"] == "Promocode already invalid"
