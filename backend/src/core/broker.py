from taskiq_aio_pika import AioPikaBroker

broker = AioPikaBroker(url="amqp://guest:guest@rabbitmq:5672/")
