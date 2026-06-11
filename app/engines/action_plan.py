class ActionPlanEngine:
    def build(
        self,
        *,
        missing_documents: list[str],
        missing_information: list[str],
        eligibility_status: str,
        scheme_name: str | None,
    ) -> dict:
        today = []
        this_week = []
        next_steps = []

        for field in missing_information[:3]:
            today.append(
                {
                    "type": "profile",
                    "title": f"Add {field.replace('.', ' ')}",
                    "reason": "This information is required for a verified eligibility decision.",
                }
            )
        for document in missing_documents[:3]:
            this_week.append(
                {
                    "type": "document",
                    "title": f"Obtain {document}",
                    "reason": f"{document} contributes to application readiness.",
                }
            )
        if eligibility_status == "eligible":
            next_steps.append(
                {
                    "type": "application",
                    "title": f"Review and apply for {scheme_name}",
                    "reason": "Your profile currently satisfies the published rules.",
                }
            )
        elif eligibility_status == "insufficient_data":
            next_steps.append(
                {
                    "type": "recheck",
                    "title": "Re-run eligibility after completing your profile",
                    "reason": "The rule engine needs the missing verified information.",
                }
            )
        else:
            next_steps.append(
                {
                    "type": "alternatives",
                    "title": "Review other matched schemes",
                    "reason": "This scheme has one or more unmet eligibility rules.",
                }
            )
        return {"today": today, "this_week": this_week, "next_steps": next_steps}

