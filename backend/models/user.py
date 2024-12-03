import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import func

from datetime import datetime


from backend.common.model import Base, id_key, get_id
from backend.utils.timezone import timezone
from .associations import user_role



class User(Base):
    id: Mapped[id_key] = mapped_column(init=False)
    x_id: Mapped[str] = mapped_column(sa.String(32), init=False, unique=True, default=get_id)
    firstname: Mapped[str] = mapped_column(sa.String, init=False, nullable=True)
    lastname: Mapped[str] = mapped_column(sa.String, init=False, index=True, nullable=True)
    phone: Mapped[str] = mapped_column(sa.String, init=False, index=True, nullable=True) 
    email: Mapped[str] = mapped_column(sa.String(200), index=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, nullable=False)
    salt: Mapped[str] = mapped_column(sa.String, nullable=True)
    status: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default='1')  # User account status (False: deactivated, True: normal)
    is_multi_login: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, default=False, server_default='1')
    last_login_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), init=False, onupdate=func.now(), default=current_timestamp())
    join_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), init=False, default=current_timestamp())

    # User related roles 
    roles: Mapped[list["Role"]] = relationship(secondary=user_role, init=False, lazy="joined")