import logging
import aiosmtplib

from email.message import EmailMessage
from core import broker
from entrypoint.config import Config

logger = logging.getLogger(__name__)


@broker.task(task_name="send_verify_email")
async def send_verify_email(config: Config, to_email: str, token):
    message = EmailMessage()
    message["From"] = config.email.USERNAME
    message["To"] = to_email
    message["Subject"] = "Verify Email"
    verify_link = config.frontend.URL + f"verify-email?{token}"
    message.set_content(f"Для активации перейдите по ссылке:\n\n{verify_link}")

    await aiosmtplib.send(
        message,
        sender=config.email.USERNAME,
        hostname=config.email.HOST,
        port=config.email.PORT,
        username=config.email.USERNAME,
        password=config.email.PASSWORD,
        use_tls=True,
        timeout=60,
        tls_context=None,
    )


@broker.task(task_name="send_otp_code")
async def send_otp_code(config: Config, to_email: str, otp_code: str):
    message = EmailMessage()
    message["From"] = config.email.USERNAME
    message["To"] = to_email
    message["Subject"] = "Verify Email"
    body = f"Ваш код для входа:\n\n{otp_code}\n\nКод действует 5 минут."
    message.set_content(body)

    await aiosmtplib.send(
        message,
        sender=config.email.USERNAME,
        hostname=config.email.HOST,
        port=config.email.PORT,
        username=config.email.USERNAME,
        password=config.email.PASSWORD,
        use_tls=True,
        timeout=60,
        tls_context=None,
    )
