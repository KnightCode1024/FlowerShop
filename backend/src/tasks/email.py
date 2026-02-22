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

    await aiosmtplib.send(
            message,
            sender=config.email.USERNAME,
            hostname=config.email.HOST,
            port=config.email.PORT,  # 465
            username=config.email.USERNAME,
            password=config.email.PASSWORD,
            use_tls=True, 
            timeout=60,  
            tls_context=None, 
        )
    