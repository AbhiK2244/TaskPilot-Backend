from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.init_db import create_db_and_tables
from app.router.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        create_db_and_tables()
    yield


app = FastAPI(
    title="TaskPilot API",
    description="A simple AI-powered task management backend.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "TaskPilot API is running", "docs": "/docs"}
