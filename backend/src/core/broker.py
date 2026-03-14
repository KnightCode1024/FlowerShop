import os

from entrypoint.config import config

if os.getenv("USE_MOCK_BROKER", "false").lower() == "true":
    from taskiq import InMemoryBroker

    broker = InMemoryBroker()
else:
    from taskiq_aio_pika import AioPikaBroker

    broker = AioPikaBroker(url=config.rabbitmq.URL)

