from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("OneTapGOV Backend Started")

    yield

    logger.info("OneTapGOV Backend Stopped")