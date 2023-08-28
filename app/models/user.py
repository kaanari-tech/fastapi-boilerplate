from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base import Base
from app.models.base import ModelBaseMixinWithoutDeletedAt


class User(ModelBaseMixinWithoutDeletedAt, Base):
    __tablename__ = "users"

    firstname: Mapped[str] = mapped_column(String(64), index=True)
    lastname: Mapped[str] = mapped_column(String(64), index=True)
    phone: Mapped[str] = mapped_column(String(), index=True)
    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="0",
    )
    password: Mapped[str] = mapped_column(Text, nullable=False)
