from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.action_plan import ActionPlanEngine
from app.models.operations import ActionPlan
from app.repositories.operations import OperationsRepository
from app.services.documents import DocumentService
from app.services.eligibility import EligibilityService


class ActionPlanService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.operations = OperationsRepository(session)
        self.eligibility = EligibilityService(session)
        self.documents = DocumentService(session)
        self.engine = ActionPlanEngine()

    async def generate(self, user_id: UUID, scheme_id: UUID) -> ActionPlan:
        eligibility = await self.eligibility.evaluate(user_id, scheme_id)
        readiness = await self.documents.readiness(user_id, scheme_id)
        plan = self.engine.build(
            missing_documents=readiness["missing_documents"],
            missing_information=eligibility.missing_information,
            eligibility_status=eligibility.status,
            scheme_name=eligibility.scheme_name,
        )
        plan["readiness_percentage"] = readiness["readiness_percentage"]
        entity = await self.operations.add(
            ActionPlan(user_id=user_id, scheme_id=scheme_id, plan=plan)
        )
        await self.session.commit()
        return entity

