import logging
import aiogram
from aiogram.exceptions import TelegramBadRequest

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
    for admin_id in config.bot.ADMINS_IDS:
        try:
            updated_at = str(invoice.updated_at) if invoice.updated_at else "N/A"
            await bot.send_message(
                chat_id=admin_id,
                text=TEMPLATE_ORDER_NOTIFY_MESSAGE.format(
                    id=invoice.uid,
                    updated_at=updated_at,
                    status=str(invoice.status),
                    user=invoice.user_id,
                    admin_link=f"{config.frontend.URL}/admin/orders/{invoice.order_id}",
                ),
            )
            print("Sent notify message for admin_id=%s", admin_id)
            logger.info("Sent notify message for admin_id=%s", admin_id)
        except TelegramBadRequest as e:
            logger.warning(
                "Skip admin notify for admin_id=%s: %s",
                admin_id,
                e,
            )
            continue
        except Exception as e:
            logger.error("Don't sent notify message for admin_id=%s", admin_id)
            raise e
    return True


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
