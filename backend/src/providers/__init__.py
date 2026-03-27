import abc

from models.invoices import Invoice


class IPaymentProvider(abc.ABC):

    @abc.abstractmethod
    async def create(self, invoice: Invoice) -> tuple[str | None, str | None]:
        pass

    @abc.abstractmethod
    async def process(self, invoice_uid: str, provider_uid: str | None = None) -> bool:
        pass
