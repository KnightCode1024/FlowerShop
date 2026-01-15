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
