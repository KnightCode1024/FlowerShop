from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import InvoiceNotFoundError
from models.invoices import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse


class IInvoiceRepository(Protocol):

    async def add(self, invoice: InvoiceCreate) -> Invoice:
        pass

    async def get(self, uid: UUID, user_id: int) -> Invoice:
        pass

    async def get_by_uid(self, uid: UUID) -> Invoice:
        pass

    async def update(self, invoice_data: InvoiceUpdate) -> Invoice:
        pass

    async def get_by_provider_uid(
        self,
        provider_uid: str,
    ) -> Invoice | None:
        pass


class InvoiceRepository(IInvoiceRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, invoice: InvoiceCreate) -> Invoice:
        obj = Invoice(**invoice.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Invoice already exists")
        return obj

    async def get(self, uid: UUID, user_id: int) -> Invoice:
        stmt = select(Invoice).where(
            Invoice.uid == uid,
            Invoice.user_id == user_id,
        )
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise InvoiceNotFoundError(uid=str(uid))

        return obj

    async def get_by_uid(self, uid: UUID) -> Invoice:
        """Get invoice by UID without user_id check (for public payment callback)."""
        stmt = select(Invoice).where(Invoice.uid == uid)
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise InvoiceNotFoundError(uid=str(uid))

        return obj

    async def update(self, invoice_data: InvoiceUpdate) -> Invoice:
        stmt = select(Invoice).where(Invoice.uid == invoice_data.uid)

        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise InvoiceNotFoundError(uid=str(invoice_data.uid))

        for key, value in invoice_data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)

        return obj

    async def get_by_provider_uid(
        self,
        provider_uid: str,
    ) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.provider_uid == provider_uid)
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()
        return obj
