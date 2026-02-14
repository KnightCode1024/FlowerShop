import time

# from email.message import EmailMessage

# import aiosmtplib
from core.broker import broker


@broker.task
async def send_verify_email():
    # message = EmailMessage()
    # message["From"] = "n17k17@yandex.ru"
    # message["To"] = "nikiforovkirill171@gmail.com"
    # message["Subject"] = "Hello World!"
    # message.set_content("Sent via aiosmtplib")

    # await aiosmtplib.send(message, hostname="smtp.yandex.ru", port=465)
    time.sleep(5)
    print("task: OK")
