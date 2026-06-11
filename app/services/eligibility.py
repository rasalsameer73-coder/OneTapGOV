from uuid import UUID

from pydantic_core import to_jsonable_python
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.engines.rules import RuleEngine
from app.models.enums import DecisionStatus
from app.models.operations import EligibilityDecision
from app.repositories.operations import OperationsRepository
from app.repositories.schemes import SchemeRepository
from app.schemas.eligibility import EligibilityResult, RuleResult
from app.services.profiles import ProfileService


class EligibilityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schemes = SchemeRepository(session)
        self.operations = OperationsRepository(session)
        self.profiles = ProfileService(session)
        self.engine = RuleEngine()

    async def evaluate(self, user_id: UUID, scheme_id: UUID) -> EligibilityResult:
        scheme = await self.schemes.get(scheme_id)
        if scheme is None or not scheme.is_active:
            raise NotFoundError("Scheme not found or inactive")
        version = await self.schemes.get_current_version(scheme)
        if version is None or not version.is_published:
            raise NotFoundError("Published scheme version not found")
        facts, _, _ = await self.profiles.facts(user_id)
        rule_rows = await self.schemes.get_rules(scheme.id)
        passed_results = []
        failed_results = []
        versions = {}
        fingerprint_source = []
        missing = set()
        for rule, rule_version in rule_rows:
            evaluation = self.engine.evaluate(rule_version.expression, facts)
            versions[rule.code] = rule_version.version_number
            fingerprint_source.append(
                {
                    "id": str(rule.id),
                    "version": rule_version.version_number,
                    "expression": rule_version.expression,
                }
            )
            result = RuleResult(
                rule_id=str(rule.id),
                code=rule.code,
                name=rule.name,
                priority=rule.priority,
                version=rule_version.version_number,
                passed=evaluation.passed,
                explanation=(
                    rule_version.explanation_pass
                    if evaluation.passed
                    else rule_version.explanation_fail
                ),
                conditions=evaluation.conditions,
            )
            for condition in evaluation.conditions:
                if condition.missing and not condition.passed:
                    missing.add(condition.field)
            (passed_results if evaluation.passed else failed_results).append(result)

        if not rule_rows:
            status = DecisionStatus.INSUFFICIENT_DATA
        elif missing and failed_results:
            status = DecisionStatus.INSUFFICIENT_DATA
        elif failed_results:
            status = DecisionStatus.NOT_ELIGIBLE
        else:
            status = DecisionStatus.ELIGIBLE
        fingerprint = self.engine.fingerprint(fingerprint_source)
        explanation = {
            "eligible_because": [item.model_dump(mode="json") for item in passed_results],
            "not_eligible_because": [item.model_dump(mode="json") for item in failed_results],
            "missing_information": sorted(missing),
            "evaluated_rule_versions": versions,
        }
        decision = await self.operations.add(
            EligibilityDecision(
                user_id=user_id,
                scheme_id=scheme.id,
                scheme_version=version.version_number,
                status=status,
                profile_snapshot=to_jsonable_python(facts),
                explanation=explanation,
                ruleset_fingerprint=fingerprint,
            )
        )
        await self.session.commit()
        await logger.ainfo(
            "eligibility_decision",
            user_id=str(user_id),
            scheme_id=str(scheme.id),
            decision_id=str(decision.id),
            status=status,
            ruleset_fingerprint=fingerprint,
        )
        return EligibilityResult(
            decision_id=str(decision.id),
            scheme_id=str(scheme.id),
            scheme_name=version.name,
            status=status,
            eligible_because=passed_results,
            not_eligible_because=failed_results,
            missing_information=sorted(missing),
            evaluated_rule_versions=versions,
            ruleset_fingerprint=fingerprint,
        )
