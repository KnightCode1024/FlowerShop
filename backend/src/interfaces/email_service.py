import abc


class IEmailService(abc.ABC):

    @abc.abstractmethod
    async def send_otp_code(self, to_email: str, otp_code: str): ...

    @abc.abstractmethod
    async def send_verify_email(self, to_email: str, token: str): ...
