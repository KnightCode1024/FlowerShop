from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from models.invoices import Invoice
from providers import IPaymentProvider
from providers.yoomoney import YoomoneyProvider
from repositories.invoice import InvoiceRepositoryI
from schemas.invoice import InvoiceCreateRequest, InvoiceCreate, Methods, InvoiceResponse
from schemas.user import UserResponse


class InvoiceService:

    def __init__(self, uow: UnitOfWork, invoices_repository: InvoiceRepositoryI, provider: IPaymentProvider):
        self.uow = uow
        self.invoices = invoices_repository
        self.provider = provider

    @require_roles([RoleEnum.USER])
    async def create_invoice(self, invoice_data: InvoiceCreateRequest, current_user: UserResponse) -> InvoiceResponse:
        invoice_data = InvoiceCreate(user_id=current_user.id, **invoice_data.model_dump())

        if invoice_data.method == Methods.YOOMONEY:
            self.provider = YoomoneyProvider()

        async with self.uow:
            invoice = await self.invoices.add(invoice_data)
            await self.provider.create(invoice)

        return InvoiceResponse(**invoice)

    @require_roles([RoleEnum.USER])
    async def process_invoice(self, uid: str, current_user: UserResponse) -> Invoice:
        async with self.uow:
            invoice = await self.invoices.get(uid, current_user.id)

        return invoice
