class RuleEvaluator:

    @staticmethod
    def evaluate(
        user_value,
        operator: str,
        rule_value,
    ) -> bool:

        if operator == "==":
            return user_value == rule_value

        if operator == "!=":
            return user_value != rule_value

        if operator == "<":
            return user_value < rule_value

        if operator == "<=":
            return user_value <= rule_value

        if operator == ">":
            return user_value > rule_value

        if operator == ">=":
            return user_value >= rule_value

        if operator == "in":
            return user_value in rule_value

        if operator == "not_in":
            return user_value not in rule_value

        if operator == "contains":
            return rule_value in user_value

        if operator == "startswith":
            return str(user_value).startswith(
                str(rule_value)
            )

        if operator == "endswith":
            return str(user_value).endswith(
                str(rule_value)
            )

        raise ValueError(
            f"Unsupported operator: {operator}"
        )