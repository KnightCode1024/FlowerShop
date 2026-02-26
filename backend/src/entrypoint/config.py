from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
env_file = find_dotenv() or (Path(__file__).resolve().parents[1] / ".env")
load_dotenv(env_file)


class PaymentsConfig(BaseSettings):
    YOOMONEY_CLIENT_ID: str
    YOOMONEY_SECRET_KEY: str
    YOOMONEY_REDIRECT_URI: str
    YOOMONEY_ACCESS_TOKEN: str


class DatabaseConfig(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    NAME: str

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
    )

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def ALEMBIC_DATABASE_URI(self) -> str:
        return f"postgresql+psycopg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class AuthJWT(BaseSettings):
    if Path("/backend/certs").exists():
        _certs_dir = Path("/backend/certs")
    else:
        _certs_dir = BASE_DIR / "certs"

    PRIVATE_KEY: Path = _certs_dir / "jwt-private.pem"
    PUBLIC_KEY: Path = _certs_dir / "jwt-public.pem"
    ALGORITM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 90  # 14


class S3Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENDPOINT: str
    PUBLIC_ENDPOINT: str
    ACCESS_KEY: str
    SECRET_KEY: str
    BUCKET_NAME: str
    REGION: str

    def get_s3_public_url(self) -> str:
        return self.PUBLIC_ENDPOINT


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: int
    HOST: str


class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EMAIL_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PORT: int = 8080
    HOST: str
    USE_SSL: bool = False
    PASSWORD: str
    USERNAME: str


class FrontendConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FRONTEND_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    URL: str


class OTPConfig(BaseSettings):
    TTL: int = 300  # seconds


class RabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    URL: str


class APPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_"
    )
    MODE: str
    NAME: str
    HOST: str
    PORT: int


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

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


config = create_config()
