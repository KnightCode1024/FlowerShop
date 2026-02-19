import abc

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.invoices import Invoice
from schemas.invoice import InvoiceCreate


class InvoiceRepositoryI(abc.ABC):

    async def add(self, invoice: InvoiceCreate) -> Invoice: pass

    async def get(self, uid: str) -> Invoice: pass


class InvoiceRepository(InvoiceRepositoryI):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, invoice: InvoiceCreate) -> Invoice:
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

    async def get(self, uid: str) -> Invoice:
        obj: Invoice | None = await self.session.get(Invoice, Invoice.uid)

        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice {uid} not found"
            )

        return obj
