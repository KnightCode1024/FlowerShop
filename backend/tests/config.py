from pathlib import Path

# from dotenv import find_dotenv, load_dotenv
# from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
# env_file = find_dotenv() or (Path(__file__).resolve().parents[1] / ".env")
# load_dotenv(env_file)


class PaymentsConfig:
    YOOMONEY_CLIENT_ID: str = "1234"
    YOOMONEY_SECRET_KEY: str = "some_secret_key"
    YOOMONEY_REDIRECT_URI: str = "http://127.0.0.1:5173"
    YOOMONEY_ACCESS_TOKEN: str = "some_access_token"


class DatabaseConfig:
    USER: str = "test_user"
    PASSWORD: str = "12345678"
    HOST: str = ""
    PORT: int = ""
    NAME: str = "test_db"

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def ALEMBIC_DATABASE_URI(self) -> str:
        return f"postgresql+psycopg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class AuthJWT:
    if Path("/backend/certs").exists():
        _certs_dir = Path("/backend/certs")
    else:
        _certs_dir = BASE_DIR / "certs"

    PRIVATE_KEY: Path = _certs_dir / "jwt-private.pem"
    PUBLIC_KEY: Path = _certs_dir / "jwt-public.pem"
    ALGORITM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 90  # 14


class S3Config:
    ENDPOINT: str = ""
    PUBLIC_ENDPOINT: str = ""
    ACCESS_KEY: str = ""
    SECRET_KEY: str = ""
    BUCKET_NAME: str = ""
    REGION: str = ""

    def get_s3_public_url(self) -> str:
        return self.PUBLIC_ENDPOINT


class RedisConfig:
    PORT: int = 6379
    HOST: str = "localhost"


class EmailConfig:
    PORT: int = 465
    HOST: str = ""
    USE_SSL: bool = True
    PASSWORD: str = "test_pass"
    USERNAME: str = "test-mail@yandex.ru"


class FrontendConfig:
    URL: str = "http://127.0.0.1:5173"


class OTPConfig:
    TTL: int = 300  # seconds


class RabbitMQConfig:
    URL: str = "amqp://guest:guest@rabbitmq:5672//"


class APPConfig:
    MODE: str = "test"
    NAME: str = "test-app"
    HOST: str = "localhost"
    PORT: int = 8000


class Config:
    database: DatabaseConfig = DatabaseConfig()
    s3: S3Config = S3Config()
    auth_jwt: AuthJWT = AuthJWT()
    redis: RedisConfig = RedisConfig()
    email: EmailConfig = EmailConfig()
    rabbitmq: RabbitMQConfig = RabbitMQConfig()
    frontend: FrontendConfig = FrontendConfig()
    app: APPConfig = APPConfig()
    otp: OTPConfig = OTPConfig()
    payment: PaymentsConfig = PaymentsConfig()


def create_config() -> Config:
    return Config()
