from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ModelBaseMixinWithoutDeletedAt


class User(ModelBaseMixinWithoutDeletedAt, Base):
    __tablename__ = "users"

    firstname: Mapped[str] = mapped_column(String(64), index=True)
    lastname: Mapped[str] = mapped_column(String(64), index=True)
    phone: Mapped[str] = mapped_column(String(), index=True)
    email: Mapped[str] = mapped_column(
        String(200), unique=True, index=True, nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="0",
    )
    password: Mapped[str] = mapped_column(Text, nullable=False)