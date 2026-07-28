from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.incidents import router as incidents_router
from app.database.db import init_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Incident Co-Pilot API")
    init_db()
    yield
    logger.info("Shutting down AI Incident Co-Pilot API")


app = FastAPI(
    title="AI Incident Co-Pilot",
    description="GenAI-powered root cause analysis and incident response assistant.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(incidents_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "AI Incident Co-Pilot"}
