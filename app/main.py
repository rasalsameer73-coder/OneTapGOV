import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan


# Load environment: prefer backend/.env if present, fall back to app/.env
backend_env = Path(__file__).parents[1] / "backend" / ".env"
if backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
else:
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# If key envs still missing, try loading with utf-16 encoding (partner formats)
if not os.getenv("SUPABASE_URL") and not os.getenv("NEXT_PUBLIC_SUPABASE_URL"):
    if backend_env.exists():
        load_dotenv(dotenv_path=backend_env, encoding="utf-16")
    else:
        load_dotenv(dotenv_path=Path(__file__).with_name(".env"), encoding="utf-16")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# Add CORS middleware (allows localhost origins by regex)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"http://(localhost|127\\.0\\.0\\.1)(:\\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount backend chat router only when Supabase envs are available to avoid import-time failures
if os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL"):
    try:
        from backend.api import chat

        app.include_router(chat.router)
    except Exception:
        # If importing backend chat fails, log and continue without it.
        import logging

        logging.getLogger("app").exception("Failed to include backend.chat router; continuing without Supabase-backed routes.")
else:
    import logging

    logging.getLogger("app").info("SUPABASE envs not found; skipping backend.chat router mount.")


@app.get("/")
async def root():
    return {"message": "OneTapGOV Backend Running"}