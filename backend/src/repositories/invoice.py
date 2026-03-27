import abc
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.invoices import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse


class InvoiceRepositoryI(abc.ABC):

    @abc.abstractmethod
    async def add(self, invoice: InvoiceCreate) -> InvoiceResponse:
        pass

    @abc.abstractmethod
    async def get(self, uid: UUID, user_id: int) -> InvoiceResponse:
        pass

    @abc.abstractmethod
    async def update(self, invoice_data: InvoiceUpdate) -> InvoiceResponse:
        pass

    @abc.abstractmethod
    async def get_by_provider_uid(self, provider_uid: str) -> InvoiceResponse | None:
        pass


class InvoiceRepository(InvoiceRepositoryI):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, invoice: InvoiceCreate) -> InvoiceResponse:
        obj = Invoice(**invoice.model_dump())
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Invoice already exists"
            )
        return obj

    async def get(self, uid: UUID, user_id: int) -> InvoiceResponse:
        stmt = select(Invoice).where(Invoice.uid == uid, Invoice.user_id == user_id)
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice {uid} not found"
            )

        return obj

    async def update(self, invoice_data: InvoiceUpdate) -> InvoiceResponse:
        stmt = select(Invoice).where(Invoice.uid == invoice_data.uid)

        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice {invoice_data.uid} not found"
            )

        for key, value in invoice_data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)

        await self.session.flush()

        return obj.to_entity()

    async def get_by_provider_uid(self, provider_uid: str) -> InvoiceResponse | None:
        stmt = select(Invoice).where(Invoice.provider_uid == provider_uid)
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()
        return obj.to_entity() if obj else None
