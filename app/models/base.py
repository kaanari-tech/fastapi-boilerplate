from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_timestamp

from app.core.logger import get_logger
from app.core.utils import get_id

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class ModelBaseMixin:
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=get_id)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=current_timestamp(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime)


class ModelBaseMixinWithoutDeletedAt:
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=get_id)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=current_timestamp(),
        onupdate=func.now(),
    )


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_deleted_at(execute_state: Any) -> None:
    """
    Automatically apply filter for logical deletion
    The following will allow you to retrieve data
    including those that have already been logically deleted
    select(...) .filter(...) .execution_options(include_deleted=True).
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            orm.with_loader_criteria(
                ModelBaseMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            ),
        )
