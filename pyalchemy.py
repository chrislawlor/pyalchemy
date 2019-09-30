from datetime import datetime
from enum import Enum
from typing import Type

import sqlalchemy as sa
from pydantic import BaseModel
from pydantic.fields import Field

COLUMN_TYPES = {
    int: sa.Integer,
    str: sa.String,
    datetime: sa.DateTime,
    bool: sa.Boolean,
    float: sa.Float,
}


def get_type_for_field(field: Field) -> type:
    """
    For optional fields, the field type_ is a :class:`typing.Union`, of
    ``NoneType`` and the actual type.

    Here we extract the "actual" type from a Union with None
    """
    if not field.sub_fields:
        return field.type_
    for f in field.sub_fields:
        if f.type_ != type(None):  # noqa
            return f.type_
    raise Exception(f"No type found for field: {field}")


def create_table(
    metadata: sa.MetaData, model: Type[BaseModel], primary_key: str = "id"
) -> sa.Table:
    """
    Create a SQLAlchemy Table from a Pydantic model.

    Caveats:

    * Models with Union types, except for Union with None, MUST all map to the
      same database column type, or bad things will probably happen.
    """
    columns = []
    for fieldname, field in model.__fields__.items():
        type_ = get_type_for_field(field)
        options = {"nullable": field.allow_none}
        if fieldname == primary_key:
            options["primary_key"] = True

        # If type is an enum, the column type is sa.Enum(type_). Otherwise,
        # look it up in the COLUMN_TYPES mapping
        if issubclass(type_, Enum):
            column_type = sa.Enum(type_)
        else:
            column_type = COLUMN_TYPES[type_]
        try:
            column = sa.Column(fieldname, column_type, **options)
        except KeyError as e:
            raise Exception(f"Unsupported type: {type_}") from e
        columns.append(column)

    tablename = model.schema()["title"].lower()
    return sa.Table(tablename, metadata, *columns)
