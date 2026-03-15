from email.message import Message, EmailMessage

import aiosmtplib

from entrypoint.config import Config, config
from interfaces import IEmailService
from interfaces.smtp_service import IStmpProvider


class SmtpProvider(IStmpProvider):

    def __init__(self, to_mail: str, subject: str, content: str, from_mail: str = config.email.USERNAME):
        self.to_mail = to_mail
        self.from_mail = from_mail
        self.subject = subject
        self.content = content

    async def send_to_mail(self) -> None:
        message = self.configure_mail()

        try:
            await aiosmtplib.send(
                message,
                sender=config.email.USERNAME,
                hostname=config.email.HOST,
                port=config.email.PORT,
                username=config.email.USERNAME,
                password=config.email.PASSWORD,
                use_tls=config.email.USE_SSL,
                timeout=60,
                tls_context=None,
            )
        except Exception as e:
            raise Exception(f"Not sent mail to {self.to_mail}") from e

    def configure_mail(self) -> Message:
        message = EmailMessage()

        message["From"] = self.from_mail
        message["To"] = self.to_mail
        message["Subject"] = self.subject

        message.set_content(self.content)

        return message
