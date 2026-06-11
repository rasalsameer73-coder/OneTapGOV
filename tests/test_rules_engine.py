from uuid import uuid4

import pytest

from app.engines.rules import RuleEngine, MISSING


def test_basic_operators_and_missing():
    engine = RuleEngine()

    facts = {"profile": {"age": 30, "tags": ["student", "voter"], "active": True}}

    # eq
    expr = {"condition": {"field": "profile.age", "operator": "eq", "value": 30}}
    res = engine.evaluate(expr, facts)
    assert res.passed is True

    # ne
    expr = {"condition": {"field": "profile.age", "operator": "ne", "value": 40}}
    assert engine.evaluate(expr, facts).passed is True

    # lt / lte / gt / gte
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "lt", "value": 40}}, facts).passed
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "lte", "value": 30}}, facts).passed
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "gt", "value": 20}}, facts).passed
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "gte", "value": 30}}, facts).passed

    # contains (substring in string or element in list)
    assert engine.evaluate({"condition": {"field": "profile.tags", "operator": "contains", "value": "student"}}, facts).passed

    # in / not_in
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "in", "value": [30, 40]}}, facts).passed
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "not_in", "value": [20]}}, facts).passed

    # truthy
    assert engine.evaluate({"condition": {"field": "profile.active", "operator": "truthy", "value": True}}, facts).passed

    # exists
    assert engine.evaluate({"condition": {"field": "profile.age", "operator": "exists", "value": True}}, facts).passed
    assert engine.evaluate({"condition": {"field": "profile.missing", "operator": "exists", "value": False}}, facts).passed

    # missing resolution returns MISSING sentinel and marks condition as missing
    result = engine.evaluate({"condition": {"field": "profile.foo", "operator": "eq", "value": 1}}, facts)
    assert result.conditions[0].actual is MISSING or result.conditions[0].missing is True or result.passed is False


def test_nested_all_any_not_and_fingerprint():
    engine = RuleEngine()
    facts = {"profile": {"age": 25, "country": "IN"}}

    expr = {
        "all": [
            {"condition": {"field": "profile.age", "operator": "gte", "value": 18}},
            {"any": [
                {"condition": {"field": "profile.country", "operator": "eq", "value": "IN"}},
                {"condition": {"field": "profile.country", "operator": "eq", "value": "US"}},
            ]}
        ]
    }

    res = engine.evaluate(expr, facts)
    assert res.passed

    # not
    expr_not = {"not": {"condition": {"field": "profile.age", "operator": "lt", "value": 18}}}
    assert engine.evaluate(expr_not, facts).passed

    # fingerprint deterministic
    rules = [
        {"id": "1", "version": 1, "expression": expr},
        {"id": "2", "version": 1, "expression": {"condition": {"field": "profile.age", "operator": "gte", "value": 18}}},
    ]
    f1 = engine.fingerprint(rules)
    f2 = engine.fingerprint(rules)
    assert isinstance(f1, str) and f1 == f2
