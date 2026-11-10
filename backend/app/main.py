"""FastAPI core application entry point for AI Office."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.logging import logger
from app.database.migrations import migration_manager
from app.providers.registry import provider_registry

# Import API routers
from app.api.health import router as health_router
from app.api.departments import router as departments_router
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.governance import router as governance_router
from app.api.events import router as events_router
from app.api.ceo import router as ceo_router
from app.api.social import router as social_router
from app.api.media_company import router as media_company_router
from app.company.employees import employee_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} on {settings.APP_HOST}:{settings.APP_PORT}...")
    
    # 1. Database Migrations
    logger.info("Verifying and applying database schema migrations...")
    applied = migration_manager.run_migrations()
    logger.info(f"Database migrations ready. Applied {len(applied)} new migrations.")

    # 2. Provider Registry Initialization
    logger.info("Initializing free-tier AI Provider Registry...")
    provider_registry.initialize()
    logger.info(f"Provider registry active with {len(provider_registry.list_all())} discovered providers.")

    # 3. Media Company Workforce Synchronization
    logger.info("Synchronizing autonomous media company employee registry...")
    employee_service.sync_registry_to_db()

    yield

    # Shutdown sequence
    logger.info("AI Office backend gracefully shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Multi-Agent Organization Control Center Backend",
    lifespan=lifespan,
)

# CORS configuration for local loopback (Android Control Center)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred.", "error_type": type(exc).__name__},
    )


# Mount API v1 Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(departments_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(governance_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(ceo_router, prefix="/api/v1")
app.include_router(social_router, prefix="/api/v1")
app.include_router(media_company_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "organization": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "api_v1": "/api/v1",
    }
