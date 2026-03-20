from pydantic import BaseModel

from models.order import *


class OrderStatus(enum.StrEnum):
    IN_CART = "in_cart"
    WAITING = "waiting"
    PAYED = "payed"
    ERROR = "error"


class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreateRequest(BaseModel):
    order_products: list[CartItem]


class OrderUpdateRequest(BaseModel):
    order_id: int
    order_products: list[CartItem]


class OrderUpdate(BaseModel):
    id: int
    user_id: int
    status: OrderStatus | None = None
    order_products: list[CartItem] | None = None


class OrderCreate(BaseModel):
    user_id: int
    order_products: list[CartItem]


class OrderResponse(BaseModel):
    id: int
    order_products: list
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
