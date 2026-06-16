from supabase import create_client
import os
import logging

_logger = logging.getLogger("supabase")


def _get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


url = _get_env("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL")
key = _get_env("SUPABASE_ANON_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY", "SUPABASE_KEY")

if not url or not key:
    _logger.warning(
        "Supabase environment variables missing; supabase client will be disabled."
    )
    supabase = None
else:
    try:
        supabase = create_client(url, key)
    except Exception:
        _logger.exception("Failed to create Supabase client; supabase disabled.")
        supabase = None


def update_table(table_name, user_id, data):
    if supabase is None:
        raise RuntimeError("Supabase client is not configured")

    return (
        supabase
        .table(table_name)
        .update(data)
        .eq("user_id", user_id)
        .execute()
    )