from pydantic import BaseModel

from src.flowershop_api.models.order import *


class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreateRequest(BaseModel):
    order_products: list[CartItem]


class OrderCreate(BaseModel):
    user_id: int
    order_products: list[CartItem]


class OrderUpdate(BaseModel):
    id: int
    status: OrderStatus | None = None
    amount: float | None = None
    order_products: list[CartItem]


class OrderResponse(BaseModel):
    id: int
    order_products: list
    amount: float
    status: OrderStatus


class OrderProductCreate(BaseModel):
    order_id: int
    order_product: CartItem


class OrderProductResponse(BaseModel):
    order_id: int
    order_products: list[CartItem]
