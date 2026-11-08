from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category_id: int = Field(gt=0)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0, default=0)
    description: Optional[str] = Field(default=None, max_length=255)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    category_id: Optional[int] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=255)


class ProductResponse(BaseModel):
    id: int
    name: str
    category_id: int
    price: float
    quantity: int
    description: Optional[str] = None
    total_value: float

    model_config = {
        "from_attributes": True
    }


class PurchaseRequest(BaseModel):
    quantity: int = Field(gt=0)


class PurchaseResponse(BaseModel):
    product_id: int
    name: str
    purchased_quantity: int
    remaining_quantity: int
    message: str


class InventoryStatistics(BaseModel):
    total_inventory_value: float
    total_products_count: int


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
