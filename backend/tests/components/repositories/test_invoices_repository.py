import random
import uuid

import pytest
from fastapi import HTTPException

from repositories import InvoiceRepository
from schemas.invoice import InvoiceCreate, InvoiceStatus, Methods, InvoiceUpdate


@pytest.mark.asyncio
async def test_create_invoice(invoice_repository: InvoiceRepository):
    invoice_data = InvoiceCreate(
        name="Pay order #1",
        order_id=1,
        user_id=1,
        amount=1234.50,
        status=InvoiceStatus.created,
        method=Methods.YOOMONEY,
    )
    invoice = await invoice_repository.add(invoice_data)

    assert invoice.amount == invoice_data.amount

    return invoice


@pytest.mark.asyncio
async def test_update_invoice_not_found(invoice_repository: InvoiceRepository):
    invoice_data = InvoiceUpdate(
        uid=uuid.uuid4(),
        status=InvoiceStatus.payed,
    )
    with pytest.raises(HTTPException) as exp:
        invoice = await invoice_repository.update(invoice_data)

        assert exp.value == f"Invoice {invoice_data.uid} not found"


@pytest.mark.asyncio
async def test_get_invoice_not_found(invoice_repository: InvoiceRepository):
    uid = uuid.uuid4()

    with pytest.raises(HTTPException) as exp:
        invoice = await invoice_repository.get(uid=uid, user_id=random.randint(1, 100))

        assert exp.value == f"Invoice {uid} not found"


@pytest.mark.asyncio
async def test_get_invoice_success(invoice_repository: InvoiceRepository):
    invoice = await test_create_invoice(invoice_repository)

    invoice_get = await invoice_repository.get(invoice.uid, invoice.user_id)

    assert invoice.uid == invoice_get.uid
