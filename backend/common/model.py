from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, declared_attr, mapped_column
from sqlalchemy import DateTime, func
from ulid import ULID
from typing import Annotated
from datetime import datetime
from sqlalchemy.sql.functions import current_timestamp



id_key = Annotated[
    int, mapped_column(primary_key=True, index=True, autoincrement=True, sort_order=-999, comment='Primary key id')
]

def get_id() -> str:
    """Create a new ULID object from the current timestamp"""
    return str(ULID()).lower()

# Mixin: A concept of object-oriented programming, makes the structure clearer, `Wiki <https://en.wikipedia.org/wiki/Mixin/>`__
class UserMixin(MappedAsDataclass):
    """User Mixin data class"""

    create_user: Mapped[int] = mapped_column(sort_order=998, comment='Creator')
    update_user: Mapped[int | None] = mapped_column(init=False, default=None, sort_order=998, comment='Updater')


class DateTimeMixin(MappedAsDataclass):
    """Datetime Mixin data class"""

    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, default=current_timestamp(), comment='Creation time'
    )
    updated_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), init=False, onupdate=func.now(),  comment='update time'
    )



class MappedBase(DeclarativeBase):
    """
    Declarative base class, the original DeclarativeBase class, exists as the parent class of all base or data model classes

    `DeclarativeBase <https://docs.sqlalchemy.org/en/20/orm/declarative_config.html>`__
    `mapped_column() <https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column>`__
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class DataClassBase(MappedAsDataclass, MappedBase):
    """
    Declarative data class base, it integrates with the data class, allowing for more advanced configuration, 
    but you must be aware of some of its features, especially when used together with DeclarativeBase

    `MappedAsDataclass <https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses>`__
    """  # noqa: E501

    __abstract__ = True


class Base(DataClassBase, DateTimeMixin):
    """
    Declarative Mixin data class base, integrates with the data class, and includes the basic table structure of the Mixin data class. 
    You can simply understand it as a base class for data classes that includes the basic table structure.
    """  # noqa: E501

    __abstract__ = True
