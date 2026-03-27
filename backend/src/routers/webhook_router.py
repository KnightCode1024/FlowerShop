from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, Header, Request

from services.invoice import InvoiceService

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
    route_class=DishkaRoute,
)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    service: FromDishka[InvoiceService],
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
):
    payload = await request.body()
    return await service.process_stripe_webhook(payload, stripe_signature)
