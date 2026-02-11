from sqladmin import ModelView

from models import *
from models.order import Order


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.created_at,
        User.updated_at,
        User.email,
        User.password,
        User.username,
        User.role,
    ]


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id,
        Product.name,
        Product.description,
        Product.price,
        Product.in_stock,
        Product.images,
        Product.category_id,
        Product.category,
    ]


class CategoryAdmin(ModelView, model=Category):
    column_list = [
        Category.id,
        Category.name,
    ]


class OrderAdmin(ModelView, model=Order):
    column_list = [
        Order.id,
        Order.user_id,
        Order.status,
        Order.amount
    ]
