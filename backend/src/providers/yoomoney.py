import abc

import aiohttp
import httpx

from entrypoint.config import config
from models.invoices import Invoice
from providers import IPaymentProvider
from schemas.invoice import InvoiceCreate


class YoomoneyProvider(IPaymentProvider):

    async def create(self, invoice: Invoice) -> str:
        async with self._get_client() as client:
            account = await self._get_account_info()
            params = {
                "label": invoice.uid,
                "sum": invoice.amount,
                "receiver": account,
                "successURL": config.payment.YOOMONEY_REDIRECT_URI,
                "quickpay-form": "button",
                "paymentType": "AC",

            }
            response = await client.post(
                url="https://yoomoney.ru/quickpay/confirm.xml?",
                params=params,
            )
        return str(response.url) if response.url else None

    async def process(self, uid: str) -> bool:
        async with self._get_client() as client:
            response = await client.post(
                url=f"https://yoomoney.ru/api/operation-history",
            )
            response.raise_for_status()

            data = await response.json()
            operations = data.get("operations", [])

            if not operations:
                return False

        for operation in operations:
            if operation.get("label") == uid:
                return True

    async def _get_account_info(self) -> str | None:
        async with self._get_client() as client:
            response = await client.post(
                url="https://yoomoney.ru/api/account-info",
            )
            response.raise_for_status()
            data = await response.json()

        return data.get("account")

    def _get_client(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {config.payment.YOOMONEY_ACCESS_TOKEN}"
            }
        )
