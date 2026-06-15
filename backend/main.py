import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

dotenv_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=dotenv_path)

if not os.getenv("SUPABASE_URL") and not os.getenv("NEXT_PUBLIC_SUPABASE_URL"):
    load_dotenv(dotenv_path=dotenv_path, encoding="utf-16")

from api import chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OneTapGov API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "OneTapGov Backend is running"}

