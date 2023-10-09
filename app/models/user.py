from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.base import ModelBaseMixinWithoutDeletedAt


class User(ModelBaseMixinWithoutDeletedAt, Base):
    firstname = Column(String(64), index=True)
    lastname = Column(String(64), index=True)
    phone = Column(String(), index=True)
    email = Column(String(200), index=True, unique=True, nullable=False)
    email_verified = Column(Boolean, nullable=False, server_default="0")
    password = Column(Text, nullable=False)
    notifications = relationship("Notification", back_populates="user")
