import pytest

from schemas.invoice import InvoiceCreateRequest, InvoiceResponse


@pytest.mark.asyncio
async def test_create_invoice(created_user_client):
    invoice = InvoiceCreateRequest(order_id=1,
                                   amount=1234)
    response = await created_user_client.post("/api/invoices/", json=invoice.model_dump())

    uid = str(response.text)

    response2 = await created_user_client.get(f"/api/invoices/{uid}")
    invoice_created = InvoiceResponse(**response2.json())

    assert invoice.amount == invoice_created.amount
