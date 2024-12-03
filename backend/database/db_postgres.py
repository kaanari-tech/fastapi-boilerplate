import sys

from typing import Annotated, Generator
from uuid import uuid4
from sqlalchemy import MetaData, create_engine

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from collections.abc import AsyncGenerator
from sqlalchemy import event


from backend.common.log import log
from backend.common.model import MappedBase
from backend.core.conf import settings
from sqlalchemy.orm import sessionmaker

    
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
)

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        future=True,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"DB connection error. detail={e}")


def create_engine_and_session(url: str | URL):
    try:
        # database engine
        engine = create_async_engine(
            url, echo=settings.POSTGRES_ECHO, future=True, pool_pre_ping=True
        )
        # log.success('Database Connection Successful')
    except Exception as e:
        log.error("❌ Database link failure {}", e)
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
        return engine, db_session


async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """session generator"""
    session = async_db_session()
    try:
        yield session
    except Exception as se:
        await session.rollback()
        raise se
    finally:
        await session.close()


# Session Annotated
CurrentSession = Annotated[AsyncSession, Depends(get_async_db)]


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


async def create_table():
    """Creating Database Tables"""
    async with async_engine.begin() as coon:
        await coon.run_sync(MappedBase.metadata.create_all)


def uuid4_str() -> str:
    """Database Engine UUID Type Compatibility Solution"""
    return str(uuid4())


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
