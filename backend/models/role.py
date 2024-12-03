from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, get_id, id_key
from backend.models.associations import user_role
from backend.models.associations import user_role

from backend.common.enums import Role as Role_enum


class Role(Base):
    """Boilerplate roles table"""

    __tablename__ = 'role'

    id: Mapped[id_key] = mapped_column(init=False)
    x_id: Mapped[str] = mapped_column(sa.String(32), init=False, unique=True, default=get_id)
    name: Mapped[str] = mapped_column(sa.String(), unique=True, default=Role_enum.USER.value, comment='role name')
    # data_scope: Mapped[int | None] = mapped_column(insert_default=2, comment='Permission ranges (1: all data permissions 2: custom data permissions)')
    status: Mapped[int] = mapped_column(sa.Integer, default=1, comment='Role status (0 deactivated 1 normal)')
    remark: Mapped[str] = mapped_column(sa.Text, default=None, comment='note')

    # Role users many-to-many
    users: Mapped[List["User"]] = relationship(
        init=False, secondary=user_role, back_populates="roles", lazy="noload"
    )
