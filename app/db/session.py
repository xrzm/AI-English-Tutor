from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_db_and_tables() -> None:
    from app.db import base  # noqa: F401
    import logging

    logger = logging.getLogger(__name__)
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Database tables ready")
    except Exception as exc:
        logger.warning("DB init skipped (tables may already exist): %s", exc)
