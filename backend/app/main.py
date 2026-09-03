"""FastAPI application main entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine, ensure_schema
from app.exceptions import OpenAIServiceError
from app.routers import insights, notes, schedule, tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup: Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(
    title="AI-Органайзер API",
    description="Backend API для умного планировщика задач с AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:18080",
        "http://localhost:80",  # prod nginx
        "http://localhost",  # prod nginx без порта
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OpenAIServiceError)
async def openai_service_error_handler(
    _request: Request,
    exc: OpenAIServiceError,
) -> JSONResponse:
    """Return a user-facing error when an OpenAI call fails."""
    logger.error("OpenAI service error: %s", str(exc))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


# Include routers
app.include_router(tasks.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(schedule.router, prefix="/api")
app.include_router(insights.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI-Органайзер API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
