import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from lab_10.models import Base, Category, Product
    from lab_10.repositories import CategoryRepository, ProductRepository
    from lab_10.services import ShopService, purchase_product
except ImportError:
    from online_store.models import Base, Category, Product
    from online_store.repositories import CategoryRepository, ProductRepository
    from online_store.services import ShopService, purchase_product


def test_models_and_repos():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        cat_repo = CategoryRepository(session)
        prod_repo = ProductRepository(session)
        service = ShopService(session)

        # Empty inventory value
        assert service.calculate_inventory_value() == 0.0
        assert service.find_most_expensive() is None

        # Add categories
        cat1 = cat_repo.add("Одяг")
        cat2 = cat_repo.add("Взуття")
        assert repr(cat1) == f"Category(id={cat1.id}, name='Одяг')"

        all_cats = cat_repo.get_all()
        assert len(all_cats) == 2
        assert cat_repo.get_by_name("Одяг") is not None
        assert cat_repo.get_by_name("Невідомо") is None

        # Add products
        p1 = Product(name="Куртка", category_id=cat1.id, price=2500.0, quantity=4)
        p2 = Product(name="Кросівки", category_id=cat2.id, price=3200.0, quantity=3)
        prod_repo.add(p1)
        prod_repo.add(p2)

        assert repr(p1) == f"Product(id={p1.id}, name='Куртка', price=2500.0, quantity=4)"
        assert p1.total_value == 10000.0

        all_prods = prod_repo.get_all()
        assert len(all_prods) == 2

        by_cat = prod_repo.find_by_category(cat1.id)
        assert len(by_cat) == 1
        assert by_cat[0].name == "Куртка"

        by_name = prod_repo.find_by_name("Кросівки")
        assert len(by_name) == 1

        # Service methods
        inv_val = service.calculate_inventory_value()
        assert inv_val == 2500.0 * 4 + 3200.0 * 3

        most_exp = service.find_most_expensive()
        assert most_exp is not None
        assert most_exp.name == "Кросівки"

        filtered = service.filter_by_category("Одяг")
        assert len(filtered) == 1

        # Purchase product errors
        with pytest.raises(ValueError, match="більшою за 0"):
            purchase_product(session, p1.id, 0)

        with pytest.raises(ValueError, match="не знайдено"):
            purchase_product(session, 99999, 1)

        with pytest.raises(ValueError, match="Недостатньо"):
            purchase_product(session, p1.id, 100)

        # Delete repo
        prod_repo.delete(p2)
        assert prod_repo.get_by_id(p2.id) is None

        cat_repo.delete(cat2)
        assert cat_repo.get_by_id(cat2.id) is None


def test_init_db_and_session():
    try:
        from lab_10.database import init_db
        from lab_10.dependencies import get_session
    except ImportError:
        from online_store.database import init_db
        from online_store.dependencies import get_session

    init_db()
    gen = get_session()
    s = next(gen)
    assert s is not None
    try:
        next(gen)
    except StopIteration:
        pass
