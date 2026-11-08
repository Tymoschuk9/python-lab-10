from __future__ import annotations

import asyncio
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

try:
    from .config import get_settings
    from .dependencies import get_session
    from .models import Category, Product
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
except (ImportError, ValueError):
    try:
        from lab_10.config import get_settings
        from lab_10.dependencies import get_session
        from lab_10.models import Category, Product
        from lab_10.repositories import CategoryRepository, ProductRepository
        from lab_10.schemas import (
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
        from lab_10.services import ShopService, purchase_product
    except ImportError:
        from config import get_settings
        from dependencies import get_session
        from models import Category, Product
        from repositories import CategoryRepository, ProductRepository
        from schemas import (
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
        from services import ShopService, purchase_product

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Laboratory work #10 (Variant 3) - Production Python: Docker, CI/CD, and Final Defense",
    version="1.0.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Shop Manager REST API is running", "environment": settings.environment, "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    current_settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=current_settings.app_name,
        environment=current_settings.environment,
    )


# --- CATEGORIES ENDPOINTS ---

@app.get("/categories", response_model=list[CategoryResponse])
async def get_categories(session: Session = Depends(get_session)) -> list[Category]:
    repo = CategoryRepository(session)
    return repo.get_all()


@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    repo = CategoryRepository(session)
    existing = repo.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Категорія '{data.name}' вже існує",
        )
    return repo.add(data.name)


@app.get("/categories/{category_id}/products", response_model=list[ProductResponse])
async def get_category_products(category_id: int, session: Session = Depends(get_session)) -> list[Product]:
    cat_repo = CategoryRepository(session)
    cat = cat_repo.get_by_id(category_id)
    if cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з id {category_id} не знайдено",
        )
    prod_repo = ProductRepository(session)
    return prod_repo.find_by_category(category_id)


# Support alternative route parameter /categories/{id}/products
@app.get("/categories/{id}/products", response_model=list[ProductResponse], include_in_schema=False)
async def get_category_products_by_id(id: int, session: Session = Depends(get_session)) -> list[Product]:
    return await get_category_products(category_id=id, session=session)


# --- PRODUCTS ENDPOINTS ---

@app.get("/products", response_model=list[ProductResponse])
async def get_products(
    category: Optional[str] = Query(default=None, description="Фільтрація за назвою категорії"),
    search: Optional[str] = Query(default=None, description="Пошук за назвою товару"),
    session: Session = Depends(get_session),
) -> list[Product]:
    service = ShopService(session)
    prod_repo = ProductRepository(session)

    if category:
        return service.filter_by_category(category)
    if search:
        return prod_repo.find_by_name(search)
    return prod_repo.get_all()


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: Session = Depends(get_session)) -> Product:
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар з id {product_id} не знайдено",
        )
    return product


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, session: Session = Depends(get_session)) -> Product:
    cat_repo = CategoryRepository(session)
    category = cat_repo.get_by_id(data.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категорію з id {data.category_id} не знайдено",
        )

    prod_repo = ProductRepository(session)
    product = Product(
        name=data.name,
        category_id=data.category_id,
        price=data.price,
        quantity=data.quantity,
        description=data.description,
    )
    return prod_repo.add(product)


@app.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
) -> Product:
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар з id {product_id} не знайдено",
        )

    updates = data.model_dump(exclude_unset=True)
    if "category_id" in updates and updates["category_id"] is not None:
        cat_repo = CategoryRepository(session)
        if not cat_repo.get_by_id(updates["category_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категорію з id {updates['category_id']} не знайдено",
            )

    for field, value in updates.items():
        setattr(product, field, value)

    session.commit()
    session.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: Session = Depends(get_session)) -> None:
    repo = ProductRepository(session)
    product = repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар з id {product_id} не знайдено",
        )
    repo.delete(product)


@app.post("/products/{product_id}/purchase", response_model=PurchaseResponse)
async def purchase_product_endpoint(
    product_id: int,
    data: PurchaseRequest,
    session: Session = Depends(get_session),
) -> PurchaseResponse:
    try:
        updated_prod = purchase_product(session, product_id, data.quantity)
        return PurchaseResponse(
            product_id=updated_prod.id,
            name=updated_prod.name,
            purchased_quantity=data.quantity,
            remaining_quantity=updated_prod.quantity,
            message="Покупку успішно здійснено",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Support alternative route /products/{id}/purchase
@app.post("/products/{id}/purchase", response_model=PurchaseResponse, include_in_schema=False)
async def purchase_product_by_id(id: int, data: PurchaseRequest, session: Session = Depends(get_session)) -> PurchaseResponse:
    return await purchase_product_endpoint(product_id=id, data=data, session=session)


# --- STATISTICS ENDPOINTS ---

@app.get("/statistics/inventory-value", response_model=InventoryStatistics)
async def get_inventory_value(session: Session = Depends(get_session)) -> InventoryStatistics:
    service = ShopService(session)
    prod_repo = ProductRepository(session)
    total_val = service.calculate_inventory_value()
    count = len(prod_repo.get_all())
    return InventoryStatistics(total_inventory_value=total_val, total_products_count=count)


@app.get("/statistics/most-expensive", response_model=ProductResponse)
async def get_most_expensive(session: Session = Depends(get_session)) -> Product:
    service = ShopService(session)
    most_exp = service.find_most_expensive()
    if most_exp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товарів на складі немає",
        )
    return most_exp
