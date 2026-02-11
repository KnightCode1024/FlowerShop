from pydantic import BaseModel

from models.order import *


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
