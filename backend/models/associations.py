import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from backend.common.model import MappedBase

user_role = sa.Table(
    "user_role",
    MappedBase.metadata,
    sa.Column(
        "id",
        sa.Integer,
        primary_key=True,
        unique=True,
        index=True,
        autoincrement=True,
        comment="Primary Key ID",
    ),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE")),
    sa.Column("role_id", sa.Integer, sa.ForeignKey("role.id", ondelete="CASCADE")),
)