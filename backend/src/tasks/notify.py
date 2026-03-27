import logging
import aiogram

from core import broker
from entrypoint.config import config
from schemas.invoice import InvoiceResponse
from schemas.order import OrderResponse
from providers.email.smtp_provider import SmtpProvider

bot = aiogram.Bot(config.bot.TOKEN, parse_mode=None)
logger = logging.getLogger(__name__)

TEMPLATE_ORDER_NOTIFY_MESSAGE: str = """
Notify about NEW order {id}

date: {updated_at}
status: {status}
user_id: {user}
link to admin: {admin_link}
"""


@broker.task(task_name="admins-user-payed-order")
async def send_notify_admins(invoice: InvoiceResponse):
    for admin_id in config.BOT_ADMINS_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=TEMPLATE_ORDER_NOTIFY_MESSAGE.format(
                    id=invoice.id,
                    status=str(invoice.status),
                    user=invoice.user_id,
                    admin_link=f"{config.frontend.URL}/admin/orders/{invoice.order_id}",
                ),
            )
        except Exception as e:
            logger.error(f"Don't sent notify message for admin_id=%s", admin_id)
            raise e


@broker.task(task_name="user-payed-order")
async def send_notify_user_to_email(to_email: str, order: OrderResponse):
    provider = SmtpProvider(
        to_mail=to_email,
        subject="Thanks for order! Your order is being processed",
        content=f"#{order.id}"
        f"Amount: {order.amount}"
        f"Status: {order.status}"
        f"Link: {config.frontend.URL}/orders/{order.id}",
    )
    await provider.send_to_mail()
