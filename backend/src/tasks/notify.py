import logging
import aiogram

from core import broker
from entrypoint.config import config
from models.invoices import Invoice
from schemas.order import OrderResponse

bot = aiogram.Bot(config.bot.TOKEN, parse_mode=None)
logger = logging.getLogger(__name__)

TEMPLATE_ORDER_NOTIFY_MESSAGE: str = """
Уведомление о новом заказе {id}   

дата: {updated_at}
статус: {status}
пользователь: {user}
ссылка на заказ в админке: {admin_link}
"""


@broker.task(task_name="user-payed-order")
async def send_notify_admins(invoice: Invoice):
    for admin_id in config.BOT_ADMINS_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=TEMPLATE_ORDER_NOTIFY_MESSAGE.format(
                    id=invoice.id,
                    status=str(invoice.status),
                    user=invoice.user_id,
                    admin_link=f"{config.frontend}/admin/orders/{invoice.order_id}",
                )
            )
        except Exception as e:
            logger.error(f"Don't sent notify message for admin_id=%s", admin_id)
