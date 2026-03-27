import pytest
from schemas.invoice import InvoiceCreateRequest, InvoiceResponse, Methods
from schemas.order import OrderCreate, OrderCreateRequest, CartItem, OrderResponse
from schemas.product import ProductResponse


@pytest.mark.asyncio
async def test_create_invoice(created_user_client, created_product: ProductResponse):
    orders_data = OrderCreateRequest(order_products=[
        CartItem(product_id=created_product.id,
                 quantity=1,
                 price=created_product.price)
    ])
    response = await created_user_client.post("/orders/", json=orders_data.model_dump())
    order = OrderResponse(**response.json())

    invoice = InvoiceCreateRequest(order_id=order.id, amount=order.amount, method=Methods.YOOMONEY)
    response = await created_user_client.post("/invoices/", json=invoice.model_dump())
    uid = str(response.text)

    response2 = await created_user_client.get(f"/invoices/{invoice.method}/{uid}")
    invoice_created = InvoiceResponse(**response2.json())

    assert invoice.amount == invoice_created.amount

    return invoice_created


