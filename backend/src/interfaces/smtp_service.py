import abc
from email.message import Message


class IStmpProvider(abc.ABC):

    @abc.abstractmethod
    async def send_to_mail(self) -> None:
        pass

    @abc.abstractmethod
    def configure_mail(self) -> Message:
        pass
