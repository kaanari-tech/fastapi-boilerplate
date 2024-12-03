from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from backend.common.model import DataClassBase, get_id, id_key
from backend.utils.timezone import timezone

class LoginLog(DataClassBase):
    """Login Log Table"""

    __tablename__ = 'login_log'

    id: Mapped[id_key] = mapped_column(init=False)
    user_x_id: Mapped[str] = mapped_column(sa.String(32))
    email: Mapped[str] = mapped_column(sa.String, comment='User email')
    status: Mapped[int] = mapped_column(sa.Integer, insert_default=0, comment='Login status (0 failed, 1 success)')
    ip: Mapped[str] = mapped_column(sa.String, comment='Login IP address')
    country: Mapped[str | None] = mapped_column(sa.String, comment='Country')
    region: Mapped[str | None] = mapped_column(sa.String, comment='Region')
    city: Mapped[str | None] = mapped_column(sa.String, comment='City')
    user_agent: Mapped[str] = mapped_column(sa.TEXT, comment='User-Agent header')  
    os: Mapped[str | None] = mapped_column(sa.String, comment='Operating system')
    browser: Mapped[str | None] = mapped_column(sa.String, comment='Browser')
    device: Mapped[str | None] = mapped_column(sa.String, comment='Device')
    msg: Mapped[str] = mapped_column(sa.TEXT, comment='Message')
    login_time: Mapped[datetime] = mapped_column(comment='Login time')
    created_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), init=False, default=func.now(), comment='Creation time')
