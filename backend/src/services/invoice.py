from typing import Dict, Callable

from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from models.invoices import Invoice
from providers import IPaymentProvider
from providers.yoomoney import YoomoneyProvider
from repositories.invoice import InvoiceRepositoryI
from schemas.invoice import InvoiceCreateRequest, InvoiceCreate, Methods, InvoiceStatus, InvoiceUpdate
from schemas.user import UserResponse


class InvoiceService:

    def __init__(self, uow: UnitOfWork, invoices_repository: InvoiceRepositoryI, provider_factories: Dict[Methods, Callable]):
        self.uow = uow
        self.invoices = invoices_repository
        self.provider_factories = provider_factories
        self.provider: IPaymentProvider = None

    @require_roles([RoleEnum.USER])
    async def create_invoice(self, invoice_data: InvoiceCreateRequest, current_user: UserResponse) -> Invoice:
        self.provider = self.provider_factories.get(Methods(invoice_data.method))()

        async with self.uow:
            invoice_data = InvoiceCreate(user_id=current_user.id, **invoice_data.model_dump())
            invoice = await self.invoices.add(invoice_data)

            link = await self.provider.create(invoice_data)

            invoice_data_update = InvoiceUpdate(uid=invoice.uid, link=link)
            invoice = await self.invoices.update(invoice_data_update)

        return invoice

    @require_roles([RoleEnum.USER])
    async def process_invoice(self, uid: str, method: str, current_user: UserResponse) -> Invoice:
        self.provider = self.provider_factories.get(Methods(method))()

        async with self.uow:
            invoice = await self.invoices.get(uid, current_user.id)

            is_payed = await self.provider.process(uid)

            invoice_data_update = InvoiceUpdate(uid=invoice.uid, status=InvoiceStatus.payed if is_payed else InvoiceStatus.processing)
            await self.invoices.update(invoice_data_update)

        return invoice
