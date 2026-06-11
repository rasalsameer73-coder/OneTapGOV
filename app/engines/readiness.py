from decimal import Decimal

from app.models.enums import DocumentStatus


class ReadinessEngine:
    AVAILABLE_STATUSES = {
        DocumentStatus.UPLOADED,
        DocumentStatus.PENDING_VERIFICATION,
        DocumentStatus.VERIFIED,
    }

    def calculate(self, requirements: list, user_documents: list) -> dict:
        latest_by_code = {}
        for document in user_documents:
            current = latest_by_code.get(document.document_code)
            if current is None or document.updated_at > current.updated_at:
                latest_by_code[document.document_code] = document

        total = sum((Decimal(item.weight) for item in requirements), Decimal("0"))
        earned = Decimal("0")
        breakdown = []
        missing = []
        for requirement in requirements:
            document = latest_by_code.get(requirement.code)
            available = bool(document and document.status in self.AVAILABLE_STATUSES)
            if available:
                earned += Decimal(requirement.weight)
            elif requirement.is_mandatory:
                missing.append(requirement.name)
            breakdown.append(
                {
                    "code": requirement.code,
                    "name": requirement.name,
                    "weight": float(requirement.weight),
                    "available": available,
                    "status": str(document.status) if document else None,
                }
            )

        percentage = float((earned / total * 100).quantize(Decimal("0.01"))) if total else 100.0
        return {
            "readiness_percentage": percentage,
            "earned_weight": float(earned),
            "total_weight": float(total),
            "breakdown": breakdown,
            "missing_documents": missing,
        }

