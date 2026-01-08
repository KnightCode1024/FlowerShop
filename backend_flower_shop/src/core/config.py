from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class DatabaseConfig(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    NAME: str

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )


class S3Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file=ENV_PATH,
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


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    HOST: str
    PORT: int
    SECRET_KEY: str


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database: DatabaseConfig = DatabaseConfig()
    s3: S3Config = S3Config()
    app: AppConfig = AppConfig()


config = Config()
