import abc

from models.invoices import Invoice
from schemas.invoice import InvoiceCreate


class IPaymentProvider(abc.ABC):

    @abc.abstractmethod
    async def create(self, invoice: Invoice) -> str:
        pass

    @abc.abstractmethod
    async def process(self, invoice_uid: str) -> bool:
        pass