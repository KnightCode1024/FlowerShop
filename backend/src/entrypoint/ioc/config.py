from dishka import Provider, provide, Scope

from entrypoint.config import Config, create_config


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_config(self) -> Config:
        config = create_config()
        return config
