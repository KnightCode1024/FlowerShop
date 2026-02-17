import taskiq_fastapi
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

# from taskiq.middlewares.taskiq_admin_middleware import TaskiqAdminMiddleware

broker = AioPikaBroker(
    url="amqp://guest:guest@rabbitmq:5672",
    queue_name="taskiq_tasks",
).with_result_backend(
    RedisAsyncResultBackend("redis://redis:6379"),
)

# .with_middlewares(
#     TaskiqAdminMiddleware(
#         url="http://taskiq_admin:3000",
#         api_token="supersecret",
#         taskiq_broker_name="mybroker",
#     )
# )
taskiq_fastapi.init(broker, "run:make_app")
