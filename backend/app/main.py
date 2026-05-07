from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.database.connection import create_tables
from app.ml.predict import model_manager
from app.models.schemas import HealthResponse
from app.routes import predict, retention, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create DB tables
    try:
        await create_tables()
    except Exception as e:
        logger.error(f"DB table creation failed: {e}")

    # Load ML model
    try:
        model_manager.load()
    except Exception as e:
        logger.error(f"Model load failed: {e}")

    # Set LangSmith env vars programmatically
    try:
        if settings.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
            os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            logger.info(
                f"LangSmith tracing enabled — project: {settings.LANGCHAIN_PROJECT}"
            )
    except Exception as e:
        logger.error(f"LangSmith setup failed: {e}")

    logger.info("ChurnShield API ready")
    yield

    # Shutdown
    logger.info("ChurnShield API shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Customer churn prediction and retention strategy API for telecom",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(retention.router)
app.include_router(history.router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        model_loaded=model_manager.is_loaded,
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )