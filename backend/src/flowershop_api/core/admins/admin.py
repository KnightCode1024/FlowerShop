from sqladmin import ModelView

from src.flowershop_api.models import *


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.created_at,
        User.updated_at,
        User.email,
        User.password,
        User.username,
        User.role,
        User.orders,
        User.orders
    ]


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id,
        Product.created_at,
        Product.updated_at,
        Product.name,
        Product.description,
        Product.price,
        Product.in_stock,
        Product.images,
        Product.category_id,
        Product.category,
        Product.quantity
    ]


class CategoryAdmin(ModelView, model=Category):
    column_list = [
        Category.id,
        Category.created_at,
        Category.updated_at,
        Category.name,
        Category.products
    ]


class OrderAdmin(ModelView, model=Order):
    column_list = [
        Order.id,
        Order.created_at,
        Order.updated_at,
        Order.order_products,
        Order.user_id,
        Order.user,
        Order.status,
        Order.amount
    ]
