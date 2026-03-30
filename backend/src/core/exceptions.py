class CategoryNotFoundError(ValueError):
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Category with id {category_id} not found")


class CategoryHasProductsError(ValueError):
    def __init__(self, category_id: int, products_count: int):
        self.category_id = category_id
        self.products_count = products_count
        super().__init__(
            f"Cannot delete category {category_id} because it has"
            f"{products_count} products. "
            "Move or delete products first."
        )


class ProductNotFoundError(ValueError):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")


class ProductNameNotUniqueError(ValueError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Product with name '{name}' already exists")


class CategoryNameNotUniqueError(ValueError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Category with name '{name}' already exists")


class OrderNotFoundError(ValueError):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")


class OrderInvalidStatusError(ValueError):
    def __init__(self, order_id: int, status: str):
        self.order_id = order_id
        self.status = status
        super().__init__(f"Order {order_id} cannot be modified in status '{status}'")


class ProductInsufficientStockError(ValueError):
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            f"Product {product_id} has insufficient stock. "
            f"Available: {available}, requested: {requested}"
        )


class ProductNotFoundErrorInOrder(ValueError):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found in order")


class PromocodeNotFoundError(ValueError):
    def __init__(self, code: str = None, promocode_id: int = None):
        self.code = code
        self.promocode_id = promocode_id
        if code:
            super().__init__(f"Promocode with code '{code}' not found")
        else:
            super().__init__(f"Promocode with id {promocode_id} not found")


class PromocodeAlreadyActivatedError(ValueError):
    def __init__(self, user_id: int, code: str):
        self.user_id = user_id
        self.code = code
        super().__init__(f"User {user_id} has already activated promocode '{code}'")


class InvoiceNotFoundError(ValueError):
    def __init__(self, uid: str = None, invoice_id: int = None):
        self.uid = uid
        self.invoice_id = invoice_id
        if uid:
            super().__init__(f"Invoice with uid '{uid}' not found")
        else:
            super().__init__(f"Invoice with id {invoice_id} not found")
