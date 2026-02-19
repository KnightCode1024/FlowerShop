from fastapi import APIRouter
from dishka import FromDishka
from schemas.invoice import InvoiceCreateRequest
from schemas.user import UserResponse
from services.invoice import InvoiceService

router = APIRouter(
    prefix="/invoices", tags=["Invoices"]
)


@router.post("/")
async def post_invoices(invoice_data: InvoiceCreateRequest,
                        service: FromDishka[InvoiceService],
                        current_user: FromDishka[UserResponse]):
    return await service.create_invoice(invoice_data, current_user)


@router.get("/{uid}")
async def get_invoice(uid: str,
                      service: FromDishka[InvoiceService],
                      current_user: FromDishka[UserResponse]):
    return await service.process_invoice(uid, current_user)
