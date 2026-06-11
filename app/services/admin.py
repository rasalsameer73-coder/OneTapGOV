from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.core.exceptions import ConflictError, NotFoundError
from app.models.operations import AuditLog
from app.models.schemes import (
    EligibilityRule,
    RequiredDocument,
    RuleVersion,
    Scheme,
    SchemeVersion,
)
from app.repositories.operations import OperationsRepository
from app.repositories.schemes import SchemeRepository
from app.schemas.scheme import (
    RequiredDocumentCreate,
    RuleCreate,
    RuleVersionCreate,
    SchemeCreate,
    SchemeUpdate,
)
from app.utils.serialization import model_dict


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schemes = SchemeRepository(session)
        self.operations = OperationsRepository(session)

    async def create_scheme(
        self, actor_id: UUID, request: SchemeCreate, trace_id: str, ip_address: str | None
    ) -> Scheme:
        if await self.schemes.get_by_code(request.code):
            raise ConflictError("Scheme code already exists")
        scheme = Scheme(
            code=request.code,
            category=request.category,
            state=request.state,
            priority=request.priority,
            is_active=request.publish,
            current_version=1,
        )
        version = SchemeVersion(
            scheme_id=scheme.id,
            version_number=1,
            name=request.name,
            description=request.description,
            authority=request.authority,
            benefit_summary=request.benefit_summary,
            application_url=str(request.application_url) if request.application_url else None,
            valid_from=request.valid_from,
            valid_until=request.valid_until,
            is_published=request.publish,
            change_note="Initial version",
        )
        await self.schemes.create_scheme(scheme, version)
        await self._audit(
            actor_id, "scheme.create", "scheme", scheme.id, None, request.model_dump(mode="json"), trace_id, ip_address
        )
        await self.session.commit()
        return scheme

    async def update_scheme(
        self,
        actor_id: UUID,
        scheme_id: UUID,
        request: SchemeUpdate,
        trace_id: str,
        ip_address: str | None,
    ) -> Scheme:
        scheme = await self._scheme(scheme_id)
        previous = await self.schemes.get_current_version(scheme)
        if previous is None:
            raise NotFoundError("Current scheme version not found")
        before = self._entity(previous)
        for field in ("category", "state", "priority"):
            value = getattr(request, field)
            if value is not None:
                setattr(scheme, field, value)
        next_version = scheme.current_version + 1
        values = {
            key: getattr(request, key) if getattr(request, key) is not None else getattr(previous, key)
            for key in (
                "name",
                "description",
                "authority",
                "benefit_summary",
                "application_url",
                "valid_from",
                "valid_until",
            )
        }
        if values["application_url"] is not None:
            values["application_url"] = str(values["application_url"])
        publish = request.publish if request.publish is not None else previous.is_published
        previous.is_published = False
        new_version = SchemeVersion(
            scheme_id=scheme.id,
            version_number=next_version,
            is_published=publish,
            change_note=request.change_note,
            **values,
        )
        scheme.current_version = next_version
        scheme.is_active = publish
        self.session.add(new_version)
        await self.session.flush()
        await self._audit(
            actor_id, "scheme.update", "scheme", scheme.id, before, self._entity(new_version), trace_id, ip_address
        )
        await self.session.commit()
        await cache.delete_pattern("recommendations:*")
        await self.session.refresh(scheme)
        return scheme

    async def set_enabled(
        self,
        actor_id: UUID,
        scheme_id: UUID,
        enabled: bool,
        trace_id: str,
        ip_address: str | None,
    ) -> Scheme:
        scheme = await self._scheme(scheme_id)
        before = {"is_active": scheme.is_active}
        scheme.is_active = enabled
        await self._audit(
            actor_id, "scheme.enable" if enabled else "scheme.disable", "scheme", scheme.id, before, {"is_active": enabled}, trace_id, ip_address
        )
        await self.session.commit()
        await cache.delete_pattern("recommendations:*")
        await self.session.refresh(scheme)
        return scheme

    async def delete_scheme(
        self, actor_id: UUID, scheme_id: UUID, trace_id: str, ip_address: str | None
    ) -> None:
        scheme = await self._scheme(scheme_id)
        scheme.is_active = False
        scheme.deleted_at = datetime.now(UTC)
        await self._audit(
            actor_id, "scheme.delete", "scheme", scheme.id, None, {"deleted_at": scheme.deleted_at.isoformat()}, trace_id, ip_address
        )
        await self.session.commit()
        await cache.delete_pattern("recommendations:*")

    async def add_rule(
        self,
        actor_id: UUID,
        scheme_id: UUID,
        request: RuleCreate,
        trace_id: str,
        ip_address: str | None,
    ) -> EligibilityRule:
        await self._scheme(scheme_id)
        rule = EligibilityRule(
            scheme_id=scheme_id,
            code=request.code,
            name=request.name,
            priority=request.priority,
            current_version=1,
        )
        version = RuleVersion(
            rule_id=rule.id,
            version_number=1,
            expression=request.expression.model_dump(by_alias=True, exclude_none=True),
            explanation_pass=request.explanation_pass,
            explanation_fail=request.explanation_fail,
            change_note=request.change_note,
        )
        await self.schemes.add_rule(rule, version)
        await self._audit(
            actor_id, "rule.create", "eligibility_rule", rule.id, None, request.model_dump(mode="json", by_alias=True), trace_id, ip_address
        )
        await self.session.commit()
        await cache.delete_pattern("recommendations:*")
        return rule

    async def add_rule_version(
        self,
        actor_id: UUID,
        rule_id: UUID,
        request: RuleVersionCreate,
        trace_id: str,
        ip_address: str | None,
    ) -> RuleVersion:
        rule = await self.schemes.get_rule(rule_id)
        if rule is None:
            raise NotFoundError("Rule not found")
        version = RuleVersion(
            rule_id=rule.id,
            version_number=rule.current_version + 1,
            expression=request.expression.model_dump(by_alias=True, exclude_none=True),
            explanation_pass=request.explanation_pass,
            explanation_fail=request.explanation_fail,
            change_note=request.change_note,
        )
        await self.schemes.add_rule_version(rule, version)
        await self._audit(
            actor_id, "rule.version.create", "eligibility_rule", rule.id, None, request.model_dump(mode="json", by_alias=True), trace_id, ip_address
        )
        await self.session.commit()
        await cache.delete_pattern("recommendations:*")
        return version

    async def add_required_document(
        self,
        actor_id: UUID,
        scheme_id: UUID,
        request: RequiredDocumentCreate,
        trace_id: str,
        ip_address: str | None,
    ) -> RequiredDocument:
        await self._scheme(scheme_id)
        document = RequiredDocument(
            scheme_id=scheme_id,
            code=request.code,
            name=request.name,
            description=request.description,
            weight=request.weight,
            is_mandatory=request.is_mandatory,
            metadata_schema=request.metadata_schema,
        )
        await self.operations.add(document)
        await self._audit(
            actor_id, "required_document.create", "required_document", document.id, None, request.model_dump(mode="json"), trace_id, ip_address
        )
        await self.session.commit()
        return document

    async def list_audit_logs(self, limit: int, offset: int) -> list[AuditLog]:
        return await self.operations.list_audit_logs(limit, offset)

    async def _scheme(self, scheme_id: UUID) -> Scheme:
        scheme = await self.schemes.get(scheme_id)
        if scheme is None or scheme.deleted_at is not None:
            raise NotFoundError("Scheme not found")
        return scheme

    async def _audit(
        self,
        actor_id: UUID,
        action: str,
        entity_type: str,
        entity_id,
        before: dict | None,
        after: dict | None,
        trace_id: str,
        ip_address: str | None,
    ) -> None:
        await self.operations.add(
            AuditLog(
                actor_user_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                before=before,
                after=after,
                trace_id=trace_id,
                ip_address=ip_address,
            )
        )

    @staticmethod
    def _entity(entity) -> dict:
        return model_dict(entity, exclude={"created_at", "updated_at"})
