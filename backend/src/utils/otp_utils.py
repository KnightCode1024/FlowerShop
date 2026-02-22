import pyotp

from entrypoint.config import config

totp = pyotp.TOTP(
    s=config.app.SECRET_KEY,
    interval=5 * 60,
)


def generate_code() -> pyotp.OTP:
    return totp.now()


def verify_code(code: pyotp.OTP) -> bool:
    return totp.verify(code)
