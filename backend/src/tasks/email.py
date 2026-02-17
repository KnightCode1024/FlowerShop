import asyncio
import logging

# import time

# from email.message import EmailMessage

# import aiosmtplib
from src.core.broker import broker

logger = logging.getLogger(__name__)

# from celery_app import celery_app


@broker.task(task_name="send_verify_email")
async def send_verify_email():
    # message = EmailMessage()
    # message["From"] = "n17k17@yandex.ru"
    # message["To"] = "nikiforovkirill171@gmail.com"
    # message["Subject"] = "Hello World!"
    # message.set_content("Sent via aiosmtplib")

    # await aiosmtplib.send(message, hostname="smtp.yandex.ru", port=465)
    await asyncio.sleep(5)
    with open("hello.txt", "w", "utf-8") as file:
        file.write("Hello!")

    print("task: OK")
