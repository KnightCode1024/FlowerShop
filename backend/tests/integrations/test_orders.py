import pytest
from httpx import AsyncClient

from schemas.order import CartItem, OrderCreateRequest, OrderResponse, OrderUpdateRequest
from schemas.promocode import PromoCreate, PromoCreateRequest, PromocodeResponse
from utils.numbers import get_percent


@pytest.mark.asyncio
async def test_order_update_with_promocode(created_user_client: AsyncClient, created_admin_client: AsyncClient, created_product):
    promocode_data = PromoCreateRequest(code="NEWYEAR",
                                        max_count_activators=102,
                                        percent=10)
    response = await created_admin_client.post("/promocodes/", json=promocode_data.model_dump())
    promocode = PromocodeResponse(**response.json())

    assert promocode.code == promocode_data.code
    assert promocode_data.percent == promocode.percent

    orders_data = OrderCreateRequest(order_products=[
        CartItem(product_id=created_product.id,
                 quantity=1,
                 price=created_product.price)
    ])
    response = await created_user_client.post("/orders/", json=orders_data.model_dump())
    order = OrderResponse(**response.json())

    order_update_data = OrderUpdateRequest(
        order_id=order.id,
        promocode=promocode.code
    )

    response2 = await created_user_client.patch(f"/orders/{order.id}", json=order_update_data.model_dump())
    updated_order = OrderResponse(**response2.json())

    assert updated_order.amount == get_percent(order.amount, promocode.percent), f"old amount - not activate promocode {promocode.percent}%"
