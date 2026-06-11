from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import (
    AgricultureProfile,
    EducationProfile,
    Profile,
    RefreshToken,
    Role,
    User,
    WomenProfile,
)
from app.core.cache import cache


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_role(self, name: str) -> Role | None:
        return await self.session.scalar(select(Role).where(Role.name == name))

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def get_by_supabase_id(self, supabase_id: UUID) -> User | None:
        return await self.session.scalar(
            select(User).where(User.supabase_user_id == supabase_id)
        )

    async def create(
        self,
        *,
        email: str,
        role_id: int,
        password_hash: str | None,
        supabase_user_id: UUID | None = None,
        is_verified: bool = False,
    ) -> User:
        user = User(
            email=email,
            role_id=role_id,
            password_hash=password_hash,
            supabase_user_id=supabase_user_id,
            is_verified=is_verified,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_profile_bundle(self, user_id: UUID) -> dict:
        models = (Profile, EducationProfile, WomenProfile, AgricultureProfile)
        values = []
        for model in models:
            values.append(
                await self.session.scalar(select(model).where(model.user_id == user_id))
            )
        return dict(zip(("profile", "education", "women", "agriculture"), values, strict=True))

    async def ensure_profile(self, user_id: UUID, name: str | None = None) -> Profile:
        profile = await self.session.scalar(select(Profile).where(Profile.user_id == user_id))
        if profile is None:
            profile = Profile(user_id=user_id, name=name)
            self.session.add(profile)
            await self.session.flush()
        return profile

    async def upsert_subprofile(self, model, user_id: UUID, values: dict):
        entity = await self.session.scalar(select(model).where(model.user_id == user_id))
        if entity is None:
            entity = model(user_id=user_id, **values)
            self.session.add(entity)
        else:
            for key, value in values.items():
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def add_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        return await self.session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

    async def revoke_token_family(self, family_id: UUID) -> None:
        tokens = (
            await self.session.scalars(
                select(RefreshToken).where(
                    RefreshToken.family_id == family_id,
                    RefreshToken.revoked_at.is_(None),
                )
            )
        ).all()
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now

    async def get_role_name(self, user: User) -> str:
        cache_key = f"role:id:{user.role_id}"
        cached = await cache.get_json(cache_key)
        if cached:
            return cached
        role = await self.session.get(Role, user.role_id)
        name = role.name if role else "citizen"
        await cache.set_json(cache_key, name, ttl_seconds=600)
        return name

