from entrypoint.config import config

from taskiq import InMemoryBroker
from taskiq_aio_pika import AioPikaBroker

if config.app.MODE == "tests":
    broker = InMemoryBroker()
else:
    broker = AioPikaBroker(url=config.rabbitmq.URL)
