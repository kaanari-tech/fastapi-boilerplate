from collections.abc import AsyncGenerator
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

try:
    engine = create_engine(
        settings.get_database_url(),
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"DB connection error. detail={e}")


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
    print(f"DB connection error. detail={e}")


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
    print("start: drop_all_tables")
    """
    Delete all tables, types, Roles, etc.
    and return to initial state (development environment only)
    """
    if settings.ENV != "dev":
        # Run only in local environnement
        print("drop_all_table() should be run only in dev env.")
        return

    metadata = MetaData()
    metadata.reflect(bind=engine)

    for table_key in metadata.tables:
        table = metadata.tables.get(table_key)
        if table is not None:
            print(f"Deleting {table_key} table")
            metadata.drop_all(engine, [table], checkfirst=True)

    print("end: drop_all_tables")
