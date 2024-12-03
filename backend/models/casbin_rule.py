from sqlalchemy import String, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import MappedBase, id_key


class CasbinRule(MappedBase):
    """Rewrite the CasbinRule model class in Casbin, using a custom Base to avoid alembic migration issues"""

    __tablename__ = 'casbin_rule'

    id: Mapped[id_key]
    ptype: Mapped[str] = mapped_column(String(255), comment='Policy type: p / g')
    v0: Mapped[str] = mapped_column(String(255), comment='Role ID / User x_id')
    v1: Mapped[str] = mapped_column(TEXT, comment='API path / Role name')
    v2: Mapped[str | None] = mapped_column(String(255), comment='Request method')
    v3: Mapped[str | None] = mapped_column(String(255))
    v4: Mapped[str | None] = mapped_column(String(255))
    v5: Mapped[str | None] = mapped_column(String(255))

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ', '.join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))
