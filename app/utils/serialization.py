from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


def json_value(value):
    if isinstance(value, (UUID, date, datetime, Decimal, Enum)):
        return str(value)
    return value


def model_dict(entity, *, exclude: set[str] | None = None) -> dict:
    excluded = exclude or set()
    return {
        column.name: json_value(
            getattr(entity, entity.__mapper__.get_property_by_column(column).key)
        )
        for column in entity.__table__.columns
        if column.name not in excluded
    }
