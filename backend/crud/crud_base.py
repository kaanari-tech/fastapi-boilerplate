from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy_crud_plus.utils import parse_filters
from sqlalchemy_crud_plus.types import Model
from sqlalchemy_crud_plus import CRUDPlus




class CRUDBase(CRUDPlus[Model]):
        
    def get_with_relationship(self, stmt: Select, populates: list[str] = [], sub_populates: list[Any] = []) -> Select:
        for populate in populates:
            stmt = stmt.options(selectinload(getattr(self.model, populate)), *sub_populates)
        
        return stmt
    
        
    async def select_model_by_column(self, session: AsyncSession, populates: list[str] = [], sub_populates: list[Any] = [], **kwargs) -> Model | None:
        """
        Query by column

        :param session: The SQLAlchemy async session.
        :param kwargs: Query expressions.
        :return:
        """
        filters = parse_filters(self.model, **kwargs)
        stmt = select(self.model).where(*filters)
        stmt = self.get_with_relationship(stmt, populates=populates, sub_populates=sub_populates)
        query = await session.execute(stmt)
        return query.scalars().first()
    