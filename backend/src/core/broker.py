__all__ = ["broker"]

from taskiq_aio_pika import AioPikaBroker

from entrypoint.config import config

broker = AioPikaBroker(
    url=config.rabbitmq.URL,
)
