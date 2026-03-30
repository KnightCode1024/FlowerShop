from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter

from schemas.invoice import InvoiceCreateRequest, InvoiceResponse, InvoiceUpdateRequest
from schemas.user import UserResponse
from services.invoice import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    route_class=DishkaRoute
)


@router.post("/", response_model=InvoiceResponse)
async def post_invoices(invoice_data: InvoiceCreateRequest,
                        service: FromDishka[InvoiceService],
                        current_user: FromDishka[UserResponse]):
    return await service.create_invoice(invoice_data, current_user)


@router.patch("/", response_model=InvoiceResponse)
async def patch_invoices(invoice_data: InvoiceUpdateRequest,
                         service: FromDishka[InvoiceService],
                         current_user: FromDishka[UserResponse]):
    return await service.update_invoice(invoice_data, current_user)


@router.get("/{method}/{uid}", response_model=InvoiceResponse)
async def get_invoice(method: str,
                      uid: str,
                      service: FromDishka[InvoiceService]):
    # Public endpoint - no authentication required for payment callback
    return await service.process_invoice(uid, method)
