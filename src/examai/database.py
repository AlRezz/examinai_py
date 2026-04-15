"""Engine and session factory."""

from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from examai.config import Settings, get_settings
from examai.models import Base

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def get_engine(settings: Optional[Settings] = None) -> Engine:
    global _engine
    if _engine is None:
        s = settings or get_settings()
        connect_args = {}
        if s.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(s.database_url, connect_args=connect_args, future=True)
    return _engine


def configure_engine(settings: Settings) -> None:
    """Reset and bind engine (tests may use in-memory SQLite with StaticPool)."""
    global _engine, _SessionLocal
    _engine = None
    _SessionLocal = None
    s = settings
    connect_args: dict = {}
    engine_kw: dict = {"future": True}
    if s.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    if ":memory:" in s.database_url:
        engine_kw["poolclass"] = StaticPool
    _engine = create_engine(
        s.database_url,
        connect_args=connect_args,
        **engine_kw,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine, future=True)


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine(), future=True
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_schema(engine: Optional[Engine] = None) -> None:
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
