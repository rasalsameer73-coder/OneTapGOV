from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Alembic Config object
config = context.config

# Allow overriding the sqlalchemy.url from the app's environment/settings
import os
try:
    # Prefer explicit env var (DATABASE_URL) or fall back to app settings
    from app.core.config import settings
    env_url = os.environ.get("DATABASE_URL") or settings.DATABASE_URL
    if env_url:
        # Alembic's offline engine expects a sync driver. If the app uses
        # an async driver (e.g. +asyncpg) convert to a sync driver for migrations.
        sync_url = env_url.replace("+asyncpg", "+psycopg")
        config.set_main_option("sqlalchemy.url", sync_url)
except Exception:
    # keep existing config if import fails or no URL present
    pass

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base
from app.core.database import Base

# Import ALL models so Alembic can discover tables
from app.modules.auth.models import User
from app.modules.profile.models import Profile

from app.modules.education.models import EducationProfile
from app.modules.women.models import WomenProfile
from app.modules.agriculture.models import AgricultureProfile
from app.modules.documents.models import SchemeDocument
from app.modules.user_documents.models import UserDocument

from app.modules.schemes.models import (
    Scheme,
    SchemeVersion,
    EligibilityRule,
    RuleCondition,
)

# Metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()