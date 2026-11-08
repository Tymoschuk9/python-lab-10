from __future__ import annotations

from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

try:
    from .models import Category, Product
except (ImportError, ValueError):
    try:
        from lab_10.models import Category, Product
    except ImportError:
        from models import Category, Product


class ShopService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def calculate_inventory_value(self) -> float:
        """Обчислює загальну вартість залишків на складі."""
        statement = select(func.sum(Product.price * Product.quantity))
        result = self.session.scalar(statement)
        if result is None:
            return 0.0
        return float(result)

    def find_most_expensive(self) -> Optional[Product]:
        """Визначає найдорожчий товар."""
        statement = (
            select(Product)
            .order_by(Product.price.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def filter_by_category(self, category_name: str) -> list[Product]:
        """Фільтрація товарів за назвою категорії."""
        statement = (
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .where(Category.name == category_name)
            .order_by(Product.name)
        )
        return list(self.session.scalars(statement))


def purchase_product(
    session: Session,
    product_id: int,
    quantity: int,
) -> Product:
    """
    Транзакційна операція купівлі товару (Lab 7 / Lab 8 / Lab 10).
    Перевіряє залишок, зменшує quantity та фіксує операцію (commit).
    При нестачі товару або помилці виконує rollback.
    """
    if quantity <= 0:
        raise ValueError("Кількість покупки повинна бути більшою за 0")

    try:
        product = session.get(Product, product_id)
        if product is None:
            raise ValueError(f"Товар із id {product_id} не знайдено")

        if product.quantity < quantity:
            raise ValueError(
                f"Недостатньо товару '{product.name}' на складі: доступно {product.quantity}, замовлено {quantity}"
            )

        product.quantity -= quantity
        session.commit()
        session.refresh(product)
        return product
    except Exception:
        session.rollback()
        raise
