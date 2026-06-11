from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import DecisionStatus


class ConditionExpression(BaseModel):
    field: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    operator: Literal[
        "eq",
        "ne",
        "lt",
        "lte",
        "gt",
        "gte",
        "in",
        "not_in",
        "contains",
        "exists",
        "truthy",
    ]
    value: Any = None


class RuleExpression(BaseModel):
    all: list["RuleNode"] | None = None
    any: list["RuleNode"] | None = None
    not_: "RuleNode | None" = Field(default=None, alias="not")
    condition: ConditionExpression | None = None

    @model_validator(mode="after")
    def exactly_one_operation(self) -> "RuleExpression":
        selected = [self.all is not None, self.any is not None, self.not_ is not None, self.condition is not None]
        if sum(selected) != 1:
            raise ValueError("Expression must contain exactly one of: all, any, not, condition")
        if self.all is not None and not self.all:
            raise ValueError("all cannot be empty")
        if self.any is not None and not self.any:
            raise ValueError("any cannot be empty")
        return self


RuleNode = RuleExpression
RuleExpression.model_rebuild()


class ConditionResult(BaseModel):
    field: str
    operator: str
    expected: Any
    actual: Any
    passed: bool
    missing: bool = False


class RuleResult(BaseModel):
    rule_id: str
    code: str
    name: str
    priority: int
    version: int
    passed: bool
    explanation: str
    conditions: list[ConditionResult]


class EligibilityResult(BaseModel):
    decision_id: str | None = None
    scheme_id: str
    scheme_name: str
    status: DecisionStatus
    eligible_because: list[RuleResult]
    not_eligible_because: list[RuleResult]
    missing_information: list[str]
    evaluated_rule_versions: dict[str, int]
    ruleset_fingerprint: str

