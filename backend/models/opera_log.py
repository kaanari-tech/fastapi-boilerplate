import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql.functions import current_timestamp

from backend.common.model import DataClassBase, get_id, id_key 



class OperaLog(DataClassBase):
    """Operation Log Table"""

    __tablename__ = 'opera_log'

    id: Mapped[id_key] = mapped_column(init=False)
    # x_id: Mapped[str] = mapped_column(sa.String(32), unique=True, insert_default=get_id)
    trace_id: Mapped[str] = mapped_column(sa.String(32), comment='Request Tracking ID')
    user_email: Mapped[str | None] = mapped_column(sa.String, comment='User Email', nullable=True)
    method: Mapped[str] = mapped_column(sa.String, comment='Request method')
    title: Mapped[str] = mapped_column(sa.String, comment='Operating module')
    path: Mapped[str] = mapped_column(sa.String, comment='Request path')
    ip: Mapped[str] = mapped_column(sa.String, comment='IP address')
    country: Mapped[str | None] = mapped_column(sa.String, comment='Country', nullable=True)
    region: Mapped[str | None] = mapped_column(sa.String, comment='Region', nullable=True)
    city: Mapped[str | None] = mapped_column(sa.String, comment='City', nullable=True)
    user_agent: Mapped[str] = mapped_column(sa.String, comment='Request header')
    os: Mapped[str] = mapped_column(sa.String, comment='Operating system')
    browser: Mapped[str] = mapped_column(sa.String, comment='Browser (software)')
    device: Mapped[str] = mapped_column(sa.String, comment='Device')
    args: Mapped[dict] = mapped_column(sa.JSON(), comment='Request Parameters')
    status: Mapped[int] = mapped_column(sa.Integer, comment='Operation status (0 abnormal 1 normal)')
    code: Mapped[str] = mapped_column(sa.String(20), insert_default='200', comment='Operation status code')
    msg: Mapped[str] = mapped_column(sa.TEXT, comment='Alert message')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='Request elapsed time (ms)')
    opera_time: Mapped[datetime] = mapped_column(comment="Operating time")
    created_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), init=False, default=current_timestamp(), comment="Creation time")