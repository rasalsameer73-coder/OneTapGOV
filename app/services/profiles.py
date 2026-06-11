from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import AgricultureProfile, EducationProfile, WomenProfile
from app.repositories.users import UserRepository
from app.schemas.profile import CompleteProfileUpdate
from app.utils.sanitization import sanitize_text


class ProfileService:
    CORE_FIELDS = (
        "name",
        "date_of_birth",
        "gender",
        "state",
        "district",
        "annual_income",
        "category",
    )

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get(self, user_id: UUID) -> dict:
        await self.users.ensure_profile(user_id)
        bundle = await self.users.get_profile_bundle(user_id)
        payload = {key: self._serialize(value) for key, value in bundle.items()}
        completion, missing = self._completion(payload)
        payload["completion_percentage"] = completion
        payload["missing_fields"] = missing
        return payload

    async def update(self, user_id: UUID, request: CompleteProfileUpdate) -> dict:
        if request.profile:
            profile = await self.users.ensure_profile(user_id)
            values = request.profile.model_dump(exclude_unset=True)
            for key, value in values.items():
                setattr(profile, key, self._clean(value))
        for request_value, model in (
            (request.education, EducationProfile),
            (request.women, WomenProfile),
            (request.agriculture, AgricultureProfile),
        ):
            if request_value:
                values = {
                    key: self._clean(value)
                    for key, value in request_value.model_dump(exclude_unset=True).items()
                }
                await self.users.upsert_subprofile(model, user_id, values)
        await self.session.commit()
        return await self.get(user_id)

    async def facts(self, user_id: UUID) -> tuple[dict, int, list[str]]:
        payload = await self.get(user_id)
        completion = payload.pop("completion_percentage")
        missing = payload.pop("missing_fields")
        profile = payload.get("profile") or {}
        dob = profile.get("date_of_birth")
        profile["age"] = self._age(dob) if dob else None
        return payload, completion, missing

    def _completion(self, payload: dict) -> tuple[int, list[str]]:
        profile = payload.get("profile") or {}
        fields = [("profile", field, profile.get(field)) for field in self.CORE_FIELDS]
        education = payload.get("education")
        if education:
            fields.extend(
                ("education", field, education.get(field))
                for field in ("course", "year", "marks")
            )
        complete = sum(value is not None and value != "" for _, _, value in fields)
        missing = [f"{section}.{field}" for section, field, value in fields if value is None or value == ""]
        return round(complete / len(fields) * 100), missing

    @staticmethod
    def _serialize(entity) -> dict | None:
        if entity is None:
            return None
        return {
            column.name: getattr(entity, column.key)
            for column in entity.__table__.columns
            if column.name not in {"id", "user_id", "created_at", "updated_at"}
        }

    @staticmethod
    def _clean(value):
        return sanitize_text(value) if isinstance(value, str) else value

    @staticmethod
    def _age(date_of_birth: date) -> int:
        today = date.today()
        return today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

