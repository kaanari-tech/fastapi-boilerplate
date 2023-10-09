from typing import Any

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy import String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_timestamp

from app.core.utils import get_id


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Generate __tablename__ automatically

    pass


class ModelBaseMixin:
    id = Column(String(32), primary_key=True, default=get_id)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=current_timestamp(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime)


class ModelBaseMixinWithoutDeletedAt:
    id = Column(String(32), primary_key=True, default=get_id)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=current_timestamp(),
    )
    updated_at = Column(
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
