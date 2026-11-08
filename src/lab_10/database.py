from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from .config import get_settings
    settings = get_settings()
    DATABASE_URL = settings.database_url
except (ImportError, ValueError):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shop.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def init_db() -> None:
    try:
        from .models import Base
    except (ImportError, ValueError):
        from models import Base
    Base.metadata.create_all(bind=engine)
