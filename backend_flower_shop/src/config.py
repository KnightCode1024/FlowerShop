from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR.parent / ".env"

# print(ENV_PATH)


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

    def get_db_url(self):
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )


# class AppConfig(BaseSettings):
#     HOST: str
#     PORT: int
#     SECRET_KEY: str

#     model_config = SettingsConfigDict(
#         env_prefix="APP_",
#         env_file=ENV_PATH,
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
    )

    database: DatabaseConfig = DatabaseConfig()
    # app: AppConfig = AppConfig()


config = Config()
