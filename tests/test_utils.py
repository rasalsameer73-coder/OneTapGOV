import pytest
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from app.utils.sanitization import sanitize_text, normalize_email
from app.utils.serialization import json_value, model_dict


class Color(Enum):
    RED = 1


def test_sanitize_text_removes_control_chars():
    raw = "hello\x00world\n "
    out = sanitize_text(raw)
    assert "\x00" not in out
    assert out == "hello\nworld"


def test_normalize_email_cases_and_whitespace():
    raw = "  UsEr@Example.COM \n"
    assert normalize_email(raw) == "user@example.com"


def test_json_value_serializes_types():
    u = uuid4()
    assert isinstance(json_value(u), str)
    assert isinstance(json_value(date.today()), str)
    assert isinstance(json_value(datetime.utcnow()), str)
    assert isinstance(json_value(Decimal("1.23")), str)
    assert isinstance(json_value(Color.RED), str)
    # non-special type passes through
    assert json_value(123) == 123


def test_model_dict_with_fake_entity():
    class Col:
        def __init__(self, name):
            self.name = name

    class Prop:
        def __init__(self, key):
            self.key = key

    class Table:
        def __init__(self, cols):
            self.columns = cols

    class Mapper:
        def __init__(self, mapping):
            self._mapping = mapping

        def get_property_by_column(self, column):
            return self._mapping[column.name]

    class Entity:
        def __init__(self):
            self.id = uuid4()
            self.amount = Decimal("2.50")
            self.name = "X"
            cols = [Col("id"), Col("amount"), Col("name")]
            self.__table__ = Table(cols)
            mapping = {"id": Prop("id"), "amount": Prop("amount"), "name": Prop("name")}
            self.__mapper__ = Mapper(mapping)

    ent = Entity()
    out = model_dict(ent)
    assert isinstance(out["id"], str)
    assert out["amount"] == str(Decimal("2.50"))
    assert out["name"] == "X"


@pytest.mark.parametrize("exclude", [None, {"b"}])
def test_model_dict_respects_exclude(exclude):
    class Col:
        def __init__(self, name):
            self.name = name

    class Prop:
        def __init__(self, key):
            self.key = key

    class Table:
        def __init__(self, cols):
            self.columns = cols

    class Mapper:
        def __init__(self, mapping):
            self._mapping = mapping

        def get_property_by_column(self, column):
            return self._mapping[column.name]

    class Entity:
        def __init__(self):
            self.a = 1
            self.b = 2
            cols = [Col("a"), Col("b")]
            self.__table__ = Table(cols)
            mapping = {"a": Prop("a"), "b": Prop("b")}
            self.__mapper__ = Mapper(mapping)

    ent = Entity()
    out = model_dict(ent, exclude=exclude)
    if exclude is None:
        assert "a" in out and "b" in out
    else:
        assert "a" in out and "b" not in out
