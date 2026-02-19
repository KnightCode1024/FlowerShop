import abc

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.invoices import Invoice
from schemas.invoice import InvoiceCreate


class InvoiceRepositoryI(abc.ABC):

    async def add(self, invoice: InvoiceCreate) -> Invoice: pass

    async def get(self, uid: str, user_id: int) -> Invoice: pass


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

    async def get(self, uid: str, user_id: int) -> Invoice:
        stmt = select(Invoice).where(Invoice.uid == uid, Invoice.user_id == user_id)
        obj: Invoice | None = (await self.session.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice {uid} not found"
            )

        return obj
