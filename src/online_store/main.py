from __future__ import annotations

import os
import uvicorn

try:
    from .api import app
    from .config import get_settings
    from .database import SessionLocal, engine
    from .models import Base, Category, Product
    from .repositories import CategoryRepository, ProductRepository
except (ImportError, ValueError):
    try:
        from lab_10.api import app
        from lab_10.config import get_settings
        from lab_10.database import SessionLocal, engine
        from lab_10.models import Base, Category, Product
        from lab_10.repositories import CategoryRepository, ProductRepository
    except ImportError:
        from api import app
        from config import get_settings
        from database import SessionLocal, engine
        from models import Base, Category, Product
        from repositories import CategoryRepository, ProductRepository


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        cat_repo = CategoryRepository(session)
        prod_repo = ProductRepository(session)

        if not cat_repo.get_all():
            elec = cat_repo.add("Електроніка")
            books = cat_repo.add("Книги")

            prod_repo.add(Product(
                name="Ноутбук",
                category_id=elec.id,
                price=32000.0,
                quantity=5,
                description="Робочий ноутбук",
            ))
            prod_repo.add(Product(
                name="Мишка бездротова",
                category_id=elec.id,
                price=750.0,
                quantity=15,
                description="Оптична мишка",
            ))
            prod_repo.add(Product(
                name="Чистий Python",
                category_id=books.id,
                price=650.0,
                quantity=20,
                description="Посібник із чистого коду",
            ))


def main() -> None:
    settings = get_settings()
    print("=" * 60)
    print(f"🚀 {settings.app_name} (Environment: {settings.environment})")
    print("=" * 60)
    init_db()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Сервер запускається на http://{host}:{port} (Swagger docs: http://{host}:{port}/docs)...")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
