import datetime
import uuid

import pytest

from schemas.invoice import InvoiceStatus, Methods, InvoiceResponse


@pytest.mark.asyncio
async def test_send_notify_admins_in_bot():
    from tasks.notify import send_notify_admins

    test_invoice_data = InvoiceResponse(
        uid=uuid.uuid4(),
        name="Test invoice",
        order_id=1,
        user_id=1,
        amount=1234,
        status=str(InvoiceStatus.payed),
        method=Methods.YOOMONEY,
        updated_at=datetime.datetime.now()
    )

    task = await send_notify_admins.kiq(test_invoice_data)
    result = await task.wait_result()
    assert result.return_value == True
