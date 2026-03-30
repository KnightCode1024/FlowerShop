import datetime
import uuid

import pytest
from httpx import AsyncClient

from schemas.invoice import InvoiceCreateRequest, InvoiceResponse, Methods, InvoiceUpdateRequest, InvoiceStatus
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

    invoice = InvoiceCreateRequest(order_id=order.id, amount=order.amount, method=Methods.STRIPE)
    response = await created_user_client.post("/invoices/", json=invoice.model_dump())
    uid = str(response.text)

    response2 = await created_user_client.get(f"/invoices/{invoice.method}/{uid}")
    invoice_created = InvoiceResponse(**response2.json())

    assert invoice.amount == invoice_created.amount

    return invoice_created


@pytest.mark.asyncio
async def test_success_invoice_and_notify_admins(created_user_client: AsyncClient, created_admin_client: AsyncClient, created_product: ProductResponse):
    orders_data = OrderCreateRequest(order_products=[
        CartItem(product_id=created_product.id,
                 quantity=1,
                 price=created_product.price)
    ])
    response = await created_user_client.post("/orders/", json=orders_data.model_dump())
    order = OrderResponse(**response.json())

    invoice = InvoiceCreateRequest(order_id=order.id, amount=order.amount, method=Methods.STRIPE)
    response = await created_user_client.post("/invoices/", json=invoice.model_dump())
    uid = str(response.text)

    invoice_update = InvoiceUpdateRequest(id=uid, status=InvoiceStatus.payed)
    response2 = await created_admin_client.patch("/invoices/", json=invoice_update.model_dump())
    invoice_updated = InvoiceResponse(**response2.json())

    assert invoice_updated.uid == uid
    assert invoice_updated.status == InvoiceStatus.payed

    response3 = await created_user_client.get(f"/invoices/{invoice.method}/{uid}")
    invoice_created = InvoiceResponse(**response3.json())

    assert invoice.amount == invoice_created.amount
    assert invoice.status == InvoiceStatus.payed

    return invoice_created


