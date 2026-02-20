import logging

from email.message import EmailMessage

import aiosmtplib
from core import broker
from entrypoint.config import config

logger = logging.getLogger(__name__)


@broker.task(task_name="send_verify_email")
async def send_verify_email(to_email: str, token):
    message = EmailMessage()
    message["From"] = config.email.USERNAME
    message["To"] = to_email
    message["Subject"] = "Verify Email"
    verify_link = config.frontend.URL + f"verify-email?{token}"
    message.set_content(f"Для активации перейдите по ссылке:\n\n{verify_link}")

    smtp_client = aiosmtplib.SMTP(
        hostname=config.email.HOST,
        port=config.email.PORT,
        use_tls=config.email.USE_TLS,
    )

    async with smtp_client:
        await smtp_client.starttls()
        await smtp_client.login(
            username=config.email.USERNAME,
            password=config.email.PASSWORD,
        )
        await smtp_client.send_message(message)
