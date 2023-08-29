import datetime
import math
from typing import Any
from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.sql import select

from .base import CRUDBase
from app.models.base import Base
from app.schemas import PagingMeta
from app.schemas import PagingQueryIn
from app.schemas import SortQueryIn

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)
ListResponseSchemaType = TypeVar("ListResponseSchemaType", bound=BaseModel)


class CRUDAsyncBase(
    CRUDBase[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ResponseSchemaType,
        ListResponseSchemaType,
    ]
):
    async def get_db_obj_by_id(
        self,
        db: AsyncSession,
        id: Any,
        include_deleted: bool = False,
    ) -> ModelType | None:
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .execution_options(include_deleted=include_deleted)
        )
        return (await db.execute(stmt)).scalars().first()

    async def get_db_obj_list(
        self,
        db: AsyncSession,
        where_clause: list[Any] | None = None,
        sort_query_in: SortQueryIn | None = None,
        include_deleted: bool = False,
    ) -> list[ModelType]:
        where_clause = where_clause if where_clause is not None else []
        stmt = select(self.model).where(*where_clause)
        if sort_query_in:
            order_by_clause = self._get_order_by_clause(sort_query_in.sort_field)
            stmt = sort_query_in.apply_to_query(stmt, order_by_clause=order_by_clause)

        db_obj_list = (
            await db.execute(stmt.execution_options(include_deleted=include_deleted))
        ).all()
        return db_obj_list

    async def get_paged_list(
        self,
        db: AsyncSession,
        paging_query_in: PagingQueryIn,
        where_clause: list[Any] | None = None,
        sort_query_in: SortQueryIn | None = None,
        include_deleted: bool = False,
    ) -> ListResponseSchemaType:
        """
        if include_deleted=True, it will all deleted object.
        """

        where_clause = where_clause if where_clause is not None else []
        stmt = (
            select(func.count(self.model.id))
            .where(*where_clause)
            .execution_options(include_deleted=include_deleted)
        )
        total_count = (await db.execute(stmt)).scalar()

        select_columns = self._get_select_columns()
        stmt = select(*select_columns).where(*where_clause)
        if sort_query_in:
            order_by_clause = self._get_order_by_clause(sort_query_in.sort_field)
            stmt = sort_query_in.apply_to_query(stmt, order_by_clause=order_by_clause)
        stmt = stmt.execution_options(include_deleted=include_deleted)
        stmt = paging_query_in.apply_to_query(stmt)
        data = (await db.execute(stmt)).all()

        meta = PagingMeta(
            total_data_count=total_count,
            current_page=paging_query_in.page,
            total_page_count=int(math.ceil(total_count / paging_query_in.per_page)),
            per_page=paging_query_in.per_page,
        )
        list_response = self.list_response_class(data=data, meta=meta)
        return list_response

    async def create(
        self,
        db: AsyncSession,
        create_schema: CreateSchemaType,
    ) -> ModelType:
        # by_alias=False else (CamenCase) will be used.
        create_dict = jsonable_encoder(create_schema, by_alias=False)
        exists_create_dict = self._filter_model_exists_fields(create_dict)
        db_obj = self.model(**exists_create_dict)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_schema: UpdateSchemaType,
    ) -> ModelType:
        # Update obj_in schema for each model column
        db_obj_dict = jsonable_encoder(db_obj)
        update_dict = update_schema.model_dump(
            exclude_unset=True,
        )
        # Unset columns are not updated when exclude_unset=True is enabled.
        for field in db_obj_dict:
            if field in update_dict:
                setattr(db_obj, field, update_dict[field])

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        """Logical suppression (soft delete)."""
        if not hasattr(db_obj, "deleted_at"):
            # Raise an exception
            print("Raise an excepton")
        if db_obj.deleted_at:
            # Raise an exception
            print("Raise an excepton")

        db_obj.deleted_at = datetime.datetime.now(tz=datetime.timezone.utc)
        await db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def real_delete(self, db: AsyncSession, db_obj: ModelType) -> None:
        """Effective suppression"""
        await db.delete(db_obj)
        await db.flush()
