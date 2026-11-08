import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from lab_10.api import app
    from lab_10.dependencies import get_session
    from lab_10.models import Base
except ImportError:
    try:
        from online_store.api import app
        from online_store.dependencies import get_session
        from online_store.models import Base
    except ImportError:
        from api import app
        from dependencies import get_session
        from models import Base


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
