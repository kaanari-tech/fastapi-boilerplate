from collections.abc import AsyncGenerator
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


try:
    engine = create_engine(
        settings.get_database_url(),
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"DB connection error. detail={e}")


try:
    async_engine = create_async_engine(
        settings.get_database_url(is_async=True),
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    async_session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
    )
except Exception as e:
    logger.error(f"DB connection error. detail={e}")


def get_db() -> Generator[Session, None, None]:
    """
    Create a database session when accessing from an endpoint, using Depend
    If there are no errors, validate.
    If there is an error, go back and close in all cases.
    """

    db = None
    try:
        db = session_factory()
        yield db
        db.commit()
    except Exception:
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
        finally:
            await db.close()


def drop_all_tables() -> None:
    logger.info("start: drop_all_tables")
    """
    Delete all tables, types, Roles, etc.
    and return to initial state (development environment only)
    """
    if settings.ENV != "dev":
        # Run only in local environnement
        logger.info("drop_all_table() should be run only in dev env.")
        return

    metadata = MetaData()
    metadata.reflect(bind=engine)

    with engine.connect() as conn:
        # Disable control of foreign key
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        # Delete all table
        for table in metadata.tables:
            conn.execute(text(f"DROP TABLE {table} CASCADE"))

        # Enable control of foreign key
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        logger.info("end: drop_all_tables")
