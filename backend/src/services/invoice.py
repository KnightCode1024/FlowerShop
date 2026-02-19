from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from models.invoices import Invoice
from providers import IPaymentProvider
from repositories.invoice import InvoiceRepository
from schemas.invoice import InvoiceCreateRequest, InvoiceCreate


class InvoiceService:

    def __init__(self, uow: UnitOfWork, repo: InvoiceRepository, provider: IPaymentProvider):
        self.uow = uow
        self.repo = repo
        self.provider = provider

    @require_roles([RoleEnum.USER])
    async def create_invoice(self, invoice_data: InvoiceCreateRequest) -> Invoice:
        invoice_data = InvoiceCreate(**invoice_data.model_dump())

        async with self.uow:
            invoice = await self.repo.add(invoice_data)
            await self.provider.create(invoice)

        return invoice

    @require_roles([RoleEnum.USER])
    async def process_invoice(self, uid: str) -> Invoice:
        async with self.uow:
            invoice = await self.repo.get(uid)

        return invoice
