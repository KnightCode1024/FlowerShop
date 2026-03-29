import uuid
from typing import Dict, Callable
from uuid import UUID

import stripe
from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from models.invoices import Invoice
from models.order import OrderStatus
from providers import IPaymentProvider
from repositories import IOrderRepository, IUserRepository
from repositories.invoice import InvoiceRepositoryI
from schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceCreate,
    Methods,
    InvoiceStatus,
    InvoiceUpdate,
    InvoiceResponse, InvoiceUpdateRequest,
)
from schemas.order import OrderUpdate
from schemas.user import UserResponse
from tasks.notify import send_notify_admins, send_notify_user_to_email
from starlette import status
from fastapi import HTTPException
from entrypoint.config import config


class InvoiceService:
    def __init__(
            self,
            uow: UnitOfWork,
            invoices_repository: InvoiceRepositoryI,
            orders_repository: IOrderRepository,
            users_repository: IUserRepository,
            provider_factories: Dict[Methods, Callable],
    ):
        self.uow = uow
        self.invoices = invoices_repository
        self.orders = orders_repository
        self.users = users_repository
        self.provider_factories = provider_factories

        self.provider: IPaymentProvider = None

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
        return invoice

    @require_roles([RoleEnum.ADMIN])
    async def update_invoice(
            self,
            invoice_data: InvoiceUpdateRequest,
    ) -> InvoiceResponse:
        async with self.uow:
            invoice_data_update = InvoiceUpdate(
                **invoice_data.model_dump()
            )
            invoice = await self.invoices.update(invoice_data_update)
        return invoice

    @require_roles([RoleEnum.USER])
    async def process_invoice(
            self, uid: str, method: str, current_user: UserResponse
    ) -> InvoiceResponse:
        uid: UUID = uuid.UUID(uid)
        self.provider = self.provider_factories.get(Methods(method))()

        async with self.uow:
            invoice = await self.invoices.get(uid, current_user.id)
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

                await send_notify_user_to_email.kiq(
                    current_user.email,
                    order.to_entity(),
                )  # sent users
                await send_notify_admins.kiq(invoice_entity)  # sent admin

                await self.orders.update(
                    OrderUpdate(
                        id=order.id, user_id=order.user_id, status=OrderStatus.PAYED
                    )
                )
        return invoice

    async def process_stripe_webhook(self, payload: bytes, signature: str | None):
        if not config.stripe.WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe webhook secret is not configured",
            )

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=config.stripe.WEBHOOK_SECRET,
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
