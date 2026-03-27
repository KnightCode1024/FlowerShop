import asyncio
from decimal import Decimal
from typing import Any

import stripe

from entrypoint.config import config
from models.invoices import Invoice
from providers import IPaymentProvider


class StripeProvider(IPaymentProvider):
    def __init__(self) -> None:
        stripe.api_key = config.stripe.SECRET_KEY

    async def create(self, invoice: Invoice) -> tuple[str | None, str | None]:
        amount = self._to_minor_units(invoice.amount, config.stripe.CURRENCY)

        def _create_session() -> Any:
            return stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": config.stripe.CURRENCY,
                            "product_data": {"name": invoice.name},
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    }
                ],
                success_url=(
                    f"{config.stripe.SUCCESS_URL}"
                    f"?invoice_uid={invoice.uid}&session_id={{CHECKOUT_SESSION_ID}}"
                ),
                cancel_url=(
                    f"{config.stripe.CANCEL_URL}"
                    f"?invoice_uid={invoice.uid}&session_id={{CHECKOUT_SESSION_ID}}"
                ),
                client_reference_id=str(invoice.uid),
                metadata={
                    "invoice_uid": str(invoice.uid),
                    "order_id": str(invoice.order_id),
                    "user_id": str(invoice.user_id),
                },
            )

        session = await asyncio.to_thread(_create_session)

        return session.url, session.id

    async def process(self, invoice_uid: str, provider_uid: str | None = None) -> bool:
        if not provider_uid:
            return False

        def _retrieve() -> Any:
            return stripe.checkout.Session.retrieve(provider_uid)

        session = await asyncio.to_thread(_retrieve)
        return session.payment_status == "paid"

    @staticmethod
    def _to_minor_units(amount: Decimal | float, currency: str) -> int:
        value = Decimal(str(amount))
        multiplier = Decimal(100)
        if currency.lower() in {"jpy", "krw"}:
            multiplier = Decimal(1)
        return int((value * multiplier).quantize(Decimal("1")))
