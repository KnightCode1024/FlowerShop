from dishka import FromDishka
from schemas.invoice import InvoiceCreateRequest, InvoiceResponse
from schemas.user import UserResponse
from services.invoice import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    route_class=DishkaRoute,
)


@router.post("/", response_model=InvoiceResponse)
async def post_invoices(invoice_data: InvoiceCreateRequest,
                        service: FromDishka[InvoiceService],
                        current_user: FromDishka[UserResponse]):
    return await service.create_invoice(invoice_data, current_user)


@router.get("/{method}/{uid}", response_model=InvoiceResponse)
async def get_invoice(method: str,
                      uid: str,
                      service: FromDishka[InvoiceService],
                      current_user: FromDishka[UserResponse]):
    return await service.process_invoice(uid, method, current_user)


@router.get("/all")
async def get_all_invoices(
    service: FromDishka[InvoiceService],
    current_user: FromDishka[UserResponse],
):
    return await service.get_all_invoices(current_user)
