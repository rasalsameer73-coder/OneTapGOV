import pytest

from app.engines.rules import RuleEngine


@pytest.fixture
def engine():
    return RuleEngine()


def condition(field, operator, value=None):
    return {"condition": {"field": field, "operator": operator, "value": value}}


def test_nested_rules_and_explanations(engine):
    facts = {
        "profile": {"income": 180000, "state": "Maharashtra", "tags": ["student"]},
        "education": {"student": True},
    }
    expression = {
        "all": [
            condition("profile.income", "lt", 200000),
            condition("profile.state", "eq", "Maharashtra"),
            {
                "any": [
                    condition("education.student", "truthy", True),
                    condition("profile.tags", "contains", "farmer"),
                ]
            },
        ]
    }
    result = engine.evaluate(expression, facts)
    assert result.passed is True
    assert len(result.conditions) == 4
    assert [item.passed for item in result.conditions] == [True, True, True, False]


@pytest.mark.parametrize(
    ("operator", "actual", "expected", "passed"),
    [
        ("eq", 2, 2, True),
        ("ne", 2, 3, True),
        ("lte", 2, 2, True),
        ("gt", 3, 2, True),
        ("gte", 3, 3, True),
        ("in", "SC", ["SC", "ST"], True),
        ("not_in", "General", ["SC", "ST"], True),
        ("contains", ["rice", "wheat"], "rice", True),
        ("truthy", 1, True, True),
    ],
)
def test_operators(engine, operator, actual, expected, passed):
    result = engine.evaluate(condition("value", operator, expected), {"value": actual})
    assert result.passed is passed


def test_missing_exists_and_not(engine):
    exists = engine.evaluate(condition("profile.income", "exists", False), {"profile": {}})
    assert exists.passed is True
    assert exists.conditions[0].missing is True
    negated = engine.evaluate(
        {"not": condition("profile.state", "eq", "Gujarat")},
        {"profile": {"state": "Maharashtra"}},
    )
    assert negated.passed is True


def test_invalid_node_and_operator(engine):
    with pytest.raises(ValueError, match="Unsupported rule node"):
        engine.evaluate({"unknown": []}, {})
    with pytest.raises(ValueError, match="Unsupported operator"):
        engine.evaluate(condition("value", "bad", 1), {"value": 1})


def test_fingerprint_is_stable(engine):
    first = engine.fingerprint([{"b": 2, "a": 1}])
    second = engine.fingerprint([{"a": 1, "b": 2}])
    assert first == second
    assert len(first) == 64

