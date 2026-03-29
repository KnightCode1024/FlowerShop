import enum

from pydantic import BaseModel


class OrderStatus(enum.StrEnum):
    IN_CART = "IN_CART"
    WAITING_PAY = "WAITING_PAY"
    PAYED = "PAYED"
    ERROR = "ERROR"


class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreateRequest(BaseModel):
    order_products: list[CartItem]


class OrderUpdateRequest(BaseModel):
    order_id: int
    order_products: list[CartItem]
    promocode: str | None = None


class OrderUpdate(BaseModel):
    id: int
    user_id: int
    status: OrderStatus | None = None
    order_products: list[CartItem] | None = None
    promocode: str | None = None
    amount: float | None = None


class OrderCreate(BaseModel):
    user_id: int
    order_products: list[CartItem]


class OrderResponse(BaseModel):
    id: int
    order_products: list[CartItem]
    amount: float
    status: OrderStatus


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
