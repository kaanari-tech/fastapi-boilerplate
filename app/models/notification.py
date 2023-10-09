from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.base import ModelBaseMixinWithoutDeletedAt


class Notification(ModelBaseMixinWithoutDeletedAt, Base):
    content = Column(Text, index=True)
    viewed = Column(Boolean, nullable=False, default=False)
    type = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user.id"))
    user = relationship("User", back_populates="notifications")
