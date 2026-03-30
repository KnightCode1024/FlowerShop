import uuid
from typing import Dict, Callable
from uuid import UUID

import stripe
from core.exceptions import InvoiceNotFoundError
from core.permissions import require_roles
from core.uow import UnitOfWork
from fastapi import HTTPException
from models import RoleEnum
from models.invoices import Invoice
from models.order import OrderStatus
from entrypoint.ioc.providers.payment import IPaymentProvider
from repositories import (
    IInvoiceRepository, 
    IOrderRepository, 
    IUserRepository, 
    IProductRepository,
)
from schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceCreate,
    Methods,
    InvoiceStatus,
    InvoiceUpdate,
    InvoiceResponse,
)
from schemas.order import OrderUpdate
from schemas.product import ProductUpdate
from schemas.user import UserResponse
from starlette import status
from tasks.notify import send_notify_admins, send_notify_user_to_email
from entrypoint.config import config as app_config


class InvoiceService:
    def __init__(
        self,
        uow: UnitOfWork,
        invoices_repository: IInvoiceRepository,
        orders_repository: IOrderRepository,
        products_repository: IProductRepository,
        users_repository: IUserRepository,
        provider_factories: Dict[Methods, Callable],
    ):
        self.uow = uow
        self.invoices = invoices_repository
        self.orders = orders_repository
        self.products = products_repository
        self.users = users_repository
        self.provider_factories = provider_factories

        # self.provider: IPaymentProvider = None

    def _to_invoice_response(self, invoice: Invoice) -> InvoiceResponse:
        return InvoiceResponse(
            uid=str(invoice.uid),
            user_id=invoice.user_id,
            order_id=invoice.order_id,
            amount=invoice.amount,
            status=invoice.status,
            method=invoice.method,
            name=invoice.name,
            link=invoice.link,
            provider_uid=invoice.provider_uid,
        )

    async def _deduct_product_quantities(self, order_id: int) -> None:
        async with self.uow:
            order = await self.orders.get(order_id, user_id=None)

            if not order or not order.order_products:
                return

            for order_product in order.order_products:
                product = await self.products.get_by_id(order_product.product_id)
                if product:
                    new_quantity = product.quantity - order_product.quantity
                    new_in_stock = new_quantity > 0
                    await self.products.update(
                        order_product.product_id,
                        ProductUpdate(
                            quantity=new_quantity,
                            in_stock=new_in_stock,
                        ),
                    )

    async def _restore_product_quantities(self, order_id: int) -> None:
        async with self.uow:
            order = await self.orders.get(order_id, user_id=None)

            if not order or not order.order_products:
                return

            for order_product in order.order_products:
                product = await self.products.get_by_id(order_product.product_id)
                if product:
                    new_quantity = product.quantity + order_product.quantity
                    new_in_stock = new_quantity > 0
                    await self.products.update(
                        order_product.product_id,
                        ProductUpdate(
                            quantity=new_quantity,
                            in_stock=new_in_stock,
                        ),
                    )

    @require_roles([RoleEnum.USER])
    async def create_invoice(
        self,
        invoice_data: InvoiceCreateRequest,
        current_user: UserResponse,
    ) -> InvoiceResponse:
        self.provider = self.provider_factories.get(
            Methods(invoice_data.method),
        )()

        name: str = f"Покупка заказа #{invoice_data.order_id}"

        async with self.uow:
            order = await self.orders.get(
                id=invoice_data.order_id, user_id=current_user.id
            )

            if order.status != OrderStatus.IN_CART:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order cannot be paid in current status",
                )

            invoice_data = InvoiceCreate(
                user_id=current_user.id,
                name=name,
                status=InvoiceStatus.created,
                amount=order.amount,
                method=invoice_data.method,
                order_id=invoice_data.order_id,
            )
            invoice = await self.invoices.add(invoice_data)

            link, provider_uid = await self.provider.create(invoice)

            invoice_data_update = InvoiceUpdate(
                uid=invoice.uid,
                link=link,
                provider_uid=provider_uid,
            )
            invoice = await self.invoices.update(invoice_data_update)

            await self.orders.update(
                OrderUpdate(
                    id=invoice.order_id,
                    user_id=invoice.user_id,
                    status=OrderStatus.WAITING_PAY,
                )
            )
        return self._to_invoice_response(invoice)

    async def process_invoice(
        self, uid: str, method: str
    ) -> InvoiceResponse:
        uid: UUID = uuid.UUID(uid)
        self.provider = self.provider_factories.get(Methods(method))()

        async with self.uow:
            invoice = await self.invoices.get_by_uid(uid)
            is_payed = await self.provider.process(str(uid), invoice.provider_uid)

            invoice_data_update = InvoiceUpdate(
                uid=invoice.uid,
                status=InvoiceStatus.payed if is_payed else InvoiceStatus.processing,
            )
            invoice_entity = await self.invoices.update(invoice_data_update)

            if is_payed:
                order = await self.orders.get(
                    id=invoice.order_id, user_id=invoice.user_id
                )
                order_entity = order.to_entity()

                user_email = ""
                try:
                    user = await self.users.get_by_id(invoice.user_id)
                    if user:
                        user_email = user.email
                except Exception:
                    pass

                await self._deduct_product_quantities(order.id)

                if user_email:
                    await send_notify_user_to_email.kiq(
                        user_email,
                        order_entity,
                    )
                await send_notify_admins.kiq(invoice_entity, order_entity)

                await self.orders.update(
                    OrderUpdate(
                        id=order.id, user_id=order.user_id, status=OrderStatus.PAYED
                    )
                )
        return self._to_invoice_response(invoice_entity)

    async def process_stripe_webhook(self, payload: bytes, signature: str | None):
        if not app_config.stripe.WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe webhook secret is not configured",
            )

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=app_config.stripe.WEBHOOK_SECRET,
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Stripe signature",
            )

        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})

        if event_type != "checkout.session.completed":
            return {"ok": True}

        session_id = data.get("id")
        payment_status = data.get("payment_status")

        if not session_id:
            return {"ok": True}

        async with self.uow:
            invoice = await self.invoices.get_by_provider_uid(session_id)
            if not invoice:
                return {"ok": True}

            if payment_status == "paid" and invoice.status != InvoiceStatus.payed:
                await self.invoices.update(
                    InvoiceUpdate(uid=UUID(invoice.uid), status=InvoiceStatus.payed)
                )

                order = await self.orders.get(
                    id=invoice.order_id,
                    user_id=invoice.user_id,
                )

                user = await self.users.get(invoice.user_id)
                if user:
                    await send_notify_user_to_email.kiq(
                        user.email,
                        order.to_entity(),
                    )
                await send_notify_admins.kiq(invoice)

                await self.orders.update(
                    OrderUpdate(
                        id=order.id,
                        user_id=order.user_id,
                        status=OrderStatus.PAYED,
                    )
                )
            elif payment_status != "paid" and invoice.status == InvoiceStatus.created:
                await self.invoices.update(
                    InvoiceUpdate(
                        uid=UUID(invoice.uid), status=InvoiceStatus.processing
                    )
                )

        return {"ok": True}
