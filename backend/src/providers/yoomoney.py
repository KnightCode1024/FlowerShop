import abc

from models.invoices import Invoice
from schemas.invoice import InvoiceCreate


class IYoomoneyProvider(abc.ABC):

    @abc.abstractmethod
    def create(self, invoice: InvoiceCreate) -> Invoice:
        pass

    @abc.abstractmethod
    def process(self, invoice_uid: str) -> bool:
        pass


class YoomoneyProvider(IYoomoneyProvider):
    pass
