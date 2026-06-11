import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.schemas.eligibility import ConditionResult

MISSING = object()


@dataclass(frozen=True)
class ExpressionEvaluation:
    passed: bool
    conditions: list[ConditionResult]


class RuleEngine:
    """Evaluates a constrained JSON AST. It intentionally never executes code."""

    def evaluate(self, expression: dict[str, Any], facts: dict[str, Any]) -> ExpressionEvaluation:
        return self._evaluate_node(expression, facts)

    def fingerprint(self, rules: list[dict[str, Any]]) -> str:
        canonical = json.dumps(rules, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _evaluate_node(
        self, node: dict[str, Any], facts: dict[str, Any]
    ) -> ExpressionEvaluation:
        if "all" in node:
            children = [self._evaluate_node(child, facts) for child in node["all"]]
            return ExpressionEvaluation(
                passed=all(child.passed for child in children),
                conditions=[item for child in children for item in child.conditions],
            )
        if "any" in node:
            children = [self._evaluate_node(child, facts) for child in node["any"]]
            return ExpressionEvaluation(
                passed=any(child.passed for child in children),
                conditions=[item for child in children for item in child.conditions],
            )
        if "not" in node:
            child = self._evaluate_node(node["not"], facts)
            return ExpressionEvaluation(passed=not child.passed, conditions=child.conditions)
        if "condition" in node:
            return self._evaluate_condition(node["condition"], facts)
        raise ValueError("Unsupported rule node")

    def _evaluate_condition(
        self, condition: dict[str, Any], facts: dict[str, Any]
    ) -> ExpressionEvaluation:
        field = condition["field"]
        operator = condition["operator"]
        expected = condition.get("value")
        actual = self._resolve(facts, field)
        missing = actual is MISSING
        passed = self._compare(actual, operator, expected)
        result = ConditionResult(
            field=field,
            operator=operator,
            expected=expected,
            actual=None if missing else actual,
            passed=passed,
            missing=missing,
        )
        return ExpressionEvaluation(passed=passed, conditions=[result])

    @staticmethod
    def _resolve(facts: dict[str, Any], field: str) -> Any:
        current: Any = facts
        for part in field.split("."):
            if not isinstance(current, dict) or part not in current:
                return MISSING
            current = current[part]
        return MISSING if current is None else current

    @staticmethod
    def _compare(actual: Any, operator: str, expected: Any) -> bool:
        if operator == "exists":
            exists = actual is not MISSING
            return exists is bool(expected)
        if actual is MISSING:
            return False
        try:
            if operator == "eq":
                return actual == expected
            if operator == "ne":
                return actual != expected
            if operator == "lt":
                return actual < expected
            if operator == "lte":
                return actual <= expected
            if operator == "gt":
                return actual > expected
            if operator == "gte":
                return actual >= expected
            if operator == "in":
                return actual in expected
            if operator == "not_in":
                return actual not in expected
            if operator == "contains":
                return expected in actual
            if operator == "truthy":
                return bool(actual) is bool(expected if expected is not None else True)
        except (TypeError, ValueError):
            return False
        raise ValueError(f"Unsupported operator: {operator}")

