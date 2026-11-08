from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

try:
    from .models import Category, Product
except (ImportError, ValueError):
    try:
        from lab_10.models import Category, Product
    except ImportError:
        from models import Category, Product


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, name: str) -> Category:
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        statement = select(Category).where(Category.name == name)
        return self.session.scalar(statement)

    def get_all(self) -> list[Category]:
        statement = select(Category).order_by(Category.name)
        return list(self.session.scalars(statement))

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.commit()


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def get_all(self) -> list[Product]:
        statement = select(Product).order_by(Product.name)
        return list(self.session.scalars(statement))

    def find_by_name(self, name: str) -> list[Product]:
        statement = select(Product).where(Product.name == name)
        return list(self.session.scalars(statement))

    def find_by_category(self, category_id: int) -> list[Product]:
        statement = select(Product).where(Product.category_id == category_id).order_by(Product.name)
        return list(self.session.scalars(statement))

    def delete(self, product: Product) -> None:
        self.session.delete(product)
        self.session.commit()
