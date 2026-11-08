from __future__ import annotations

from .api import app
from .config import Settings, get_settings
from .database import SessionLocal, engine, init_db
from .models import Base, Category, Product
from .repositories import CategoryRepository, ProductRepository
from .schemas import (
    CategoryCreate,
    CategoryResponse,
    HealthResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    PurchaseRequest,
    PurchaseResponse,
    InventoryStatistics,
)
from .services import ShopService, purchase_product

__all__ = [
    "app",
    "Base",
    "Category",
    "Product",
    "CategoryRepository",
    "ProductRepository",
    "ShopService",
    "purchase_product",
    "SessionLocal",
    "engine",
    "init_db",
    "get_settings",
    "Settings",
    "CategoryCreate",
    "CategoryResponse",
    "HealthResponse",
    "ProductCreate",
    "ProductResponse",
    "ProductUpdate",
    "PurchaseRequest",
    "PurchaseResponse",
    "InventoryStatistics",
]
