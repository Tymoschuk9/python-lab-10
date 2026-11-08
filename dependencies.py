from __future__ import annotations

from collections.abc import Generator
from sqlalchemy.orm import Session

try:
    from .database import SessionLocal
except (ImportError, ValueError):
    try:
        from lab_10.database import SessionLocal
    except ImportError:
        from database import SessionLocal


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
