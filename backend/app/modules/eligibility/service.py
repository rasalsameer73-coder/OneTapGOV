from app.modules.eligibility.context_builder import (
    UserContextBuilder,
)
from app.modules.eligibility.evaluator import (
    RuleEvaluator,
)
from app.modules.eligibility.schemas import (
    EligibleSchemeResponse,
)

from app.modules.schemes.repository import (
    SchemeRepository,
)

from app.modules.profile.repository import (
    ProfileRepository,
)
from app.modules.education.repository import (
    EducationRepository,
)
from app.modules.women.repository import (
    WomenRepository,
)
from app.modules.agriculture.repository import (
    AgricultureRepository,
)


class EligibilityService:

    def __init__(
        self,
        scheme_repository: SchemeRepository,
        profile_repository: ProfileRepository,
        education_repository: EducationRepository,
        women_repository: WomenRepository,
        agriculture_repository: AgricultureRepository,
    ):
        self.scheme_repository = scheme_repository
        self.profile_repository = profile_repository
        self.education_repository = education_repository
        self.women_repository = women_repository
        self.agriculture_repository = agriculture_repository

    async def get_eligible_schemes(
        self,
        current_user,
    ) -> list[EligibleSchemeResponse]:

        # Load profile data
        profile = await self.profile_repository.get_by_user_id(
            current_user.id
        )

        education = await self.education_repository.get_by_user_id(
            current_user.id
        )

        women = await self.women_repository.get_by_user_id(
            current_user.id
        )

        agriculture = await self.agriculture_repository.get_by_user_id(
            current_user.id
        )

        # Build user context
        user_context = UserContextBuilder.build(
            profile,
            education,
            women,
            agriculture,
        )

        eligible_schemes = []

        schemes = await self.scheme_repository.get_all_schemes()

        for scheme in schemes:

            total_conditions = 0
            passed_conditions = 0

            versions = await self.scheme_repository.get_scheme_versions(
                scheme.id
            )

            scheme_is_eligible = False

            for version in versions:

                rules = await self.scheme_repository.get_eligibility_rules(
                    version.id
                )

                all_rules_passed = True

                for rule in rules:

                    conditions = (
                        await self.scheme_repository.get_rule_conditions(
                            rule.id
                        )
                    )

                    for condition in conditions:

                        total_conditions += 1

                        user_value = user_context.get(
                            condition.field_name
                        )

                        rule_value = condition.comparison_value

                        # Convert bool strings
                        if isinstance(rule_value, str):

                            if rule_value.lower() == "true":
                                rule_value = True

                            elif rule_value.lower() == "false":
                                rule_value = False

                            else:
                                try:
                                    rule_value = float(rule_value)
                                except ValueError:
                                    pass

                        passed = RuleEvaluator.evaluate(
                            user_value,
                            condition.comparison_operator,
                            rule_value,
                        )

                        if passed:
                            passed_conditions += 1

                        if not passed:
                            all_rules_passed = False
                            break

                    if not all_rules_passed:
                        break

                if all_rules_passed:
                    scheme_is_eligible = True
                    break

            if total_conditions == 0:
                match_score = 0
            else:
                match_score = int(
                    passed_conditions
                    / total_conditions
                    * 100
                )

            if scheme_is_eligible:

                eligible_schemes.append(
                    EligibleSchemeResponse(
                        scheme_id=scheme.id,
                        scheme_name=scheme.scheme_name,
                        match_score=match_score,
                    )
                )

        return eligible_schemes