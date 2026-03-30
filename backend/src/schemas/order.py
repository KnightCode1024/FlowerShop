import enum

from pydantic import BaseModel, Field


class OrderStatus(enum.StrEnum):
    IN_CART = "IN_CART"
    WAITING_PAY = "WAITING_PAY"
    PAYED = "PAYED"
    ERROR = "ERROR"


class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class DeliveryAddress(BaseModel):
    recipient_name: str = Field(..., min_length=1, max_length=255)
    recipient_phone: str = Field(..., min_length=5, max_length=50)
    delivery_address: str = Field(..., min_length=5, max_length=500)
    delivery_city: str = Field(..., min_length=1, max_length=100)
    delivery_zip: str | None = Field(None, max_length=20)
    delivery_notes: str | None = Field(None, max_length=1000)


class OrderCreateRequest(BaseModel):
    order_products: list[CartItem]
    delivery_address: DeliveryAddress | None = None


class OrderUpdateRequest(BaseModel):
    order_id: int
    order_products: list[CartItem]
    delivery_address: DeliveryAddress | None = None
    promocode: str | None = None


class OrderUpdate(BaseModel):
    id: int
    user_id: int
    status: OrderStatus | None = None
    order_products: list[CartItem] | None = None
    recipient_name: str | None = None
    recipient_phone: str | None = None
    delivery_address: str | None = None
    delivery_city: str | None = None
    delivery_zip: str | None = None
    delivery_notes: str | None = None
    promocode: str | None = None
    amount: float | None = None


class OrderCreate(BaseModel):
    user_id: int
    order_products: list[CartItem]
    recipient_name: str | None = None
    recipient_phone: str | None = None
    delivery_address: str | None = None
    delivery_city: str | None = None
    delivery_zip: str | None = None
    delivery_notes: str | None = None


class OrderResponse(BaseModel):
    id: int
    order_products: list[CartItem]
    amount: float
    status: OrderStatus
    recipient_name: str | None = None
    recipient_phone: str | None = None
    delivery_address: str | None = None
    delivery_city: str | None = None
    delivery_zip: str | None = None
    delivery_notes: str | None = None


class OrderProductCreate(BaseModel):
    user_id: int
    order_product: CartItem


class OrderProductResponse(BaseModel):
    user_id: int
    order_products: list[CartItem]


class OrdersAnalytics(BaseModel):
    count_orders: int | None = None
    count_1_days_orders: int | None = None
    count_7_days_orders: int | None = None
    count_30_days_orders: int | None = None

    amount_for_all_orders: float | None = None
    amount_for_1_days_orders: float | None = None
    amount_for_7_days_orders: float | None = None
    amount_for_30_days_orders: float | None = None
