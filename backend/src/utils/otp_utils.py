import pyotp

from entrypoint.config import config


def generate_otp_secret() -> str:
    return pyotp.random_base32()


def generate_otp_code(otp_secret: str) -> str:
    totp = pyotp.TOTP(s=otp_secret, interval=config.otp.TTL)
    return totp.now()


def verify_otp_code(code: str, otp_secret: str) -> bool:
    totp = pyotp.TOTP(s=otp_secret, interval=config.otp.TTL)
    return totp.verify(code)
