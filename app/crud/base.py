from enum import Enum
from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)
ListResponseSchemaType = TypeVar("ListResponseSchemaType", bound=BaseModel)


class CRUDBase(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ResponseSchemaType,
        ListResponseSchemaType,
    ]
):
    def __init__(
        self,
        model: type[ModelType],
        response_schema_class: type[ResponseSchemaType],
        list_response_class: type[ListResponseSchemaType],
    ) -> None:
        self.model = model
        self.response_schema_class = response_schema_class
        self.list_response_class = list_response_class

    def _get_select_columns(self) -> list[ColumnProperty]:
        """
        only field in ResponseSchema will be return as object for sqlalchemy select
        """
        schema_columns = list(self.response_schema_class.model_fields.keys())
        mapper = inspect(self.model)
        select_columns = [
            getattr(self.model, attr.key)
            for attr in mapper.attrs
            if isinstance(attr, ColumnProperty) and attr.key in schema_columns
        ]

        return select_columns

    def _filter_model_exists_fields(self, data_dict: dict[str, Any]) -> dict[str, Any]:
        """
        filter self.model and return all field available on data_dict
        """
        data_fields = list(data_dict.keys())
        mapper = inspect(self.model)
        exists_data_dict = {}
        for attr in mapper.attrs:
            if isinstance(attr, ColumnProperty) and attr.key in data_fields:
                exists_data_dict[attr.key] = data_dict[attr.key]

        return exists_data_dict

    def _get_order_by_clause(
        self,
        sort_field: Any | Enum,
    ) -> ColumnProperty | None:
        sort_field_value = (
            sort_field.value if isinstance(sort_field, Enum) else sort_field
        )
        mapper = inspect(self.model)
        order_by_clause = [
            attr
            for attr in mapper.attrs
            if isinstance(attr, ColumnProperty) and attr.key == sort_field_value
        ]

        return order_by_clause[0] if order_by_clause else None
