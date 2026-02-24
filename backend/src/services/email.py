from entrypoint.config import Config
from interfaces import IEmailService
from tasks.email import send_otp_code, send_verify_email


class EmailService(IEmailService):
    def __init__(self, config: Config):
        self.config = config

    async def send_otp_code(self, to_email: str, otp_code: str):
        await send_otp_code.kiq(self.config, to_email, otp_code)

    async def send_verify_email(self, to_email: str, token: str):
        await send_verify_email.kiq(self.config, to_email, token)
