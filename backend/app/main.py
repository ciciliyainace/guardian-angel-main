from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging_config import setup_logging, logger
from app.core.database import db_manager, init_indexes
from app.core.exceptions import (
    SentinelAIException,
    ProtectedTargetError,
    PermissionDeniedError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    FirewallExecutionError,
)
from app.api.v1.router import api_router
from app.api.v1.endpoints import health as health_endpoint
from app.workers.ingestion_worker import ingestion_worker
from app.workers.expiry_worker import expiry_worker
from app.workers.detection_worker import detection_worker
from app.ml.registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    setup_logging()
    logger.info("Initializing SentinelAI Backend Defense System...")

    # Connect to MongoDB Atlas and initialize collection indexes
    connected = db_manager.connect()
    if connected:
        init_indexes(db_manager.get_db())
    else:
        logger.warning(
            f"MongoDB Atlas is currently unreachable ({db_manager.last_error}). "
            "Backend will report database as unavailable. Verify MONGODB_URI in backend/.env."
        )

    # Load ML Model Artifacts
    registry.reload_all()

    # Start Background Workers only in normal mode, not during test runs or if disabled
    import os
    is_testing = os.environ.get("TESTING") == "true"
    enable_workers = settings.ENABLE_BACKGROUND_WORKERS and not is_testing
    if enable_workers:
        ingestion_worker.start()
        expiry_worker.start()
        detection_worker.start()

    logger.info("SentinelAI Backend online and operational.")
    yield

    # Shutdown sequence
    logger.info("Shutting down SentinelAI Backend...")
    if enable_workers:
        ingestion_worker.stop()
        expiry_worker.stop()
        detection_worker.stop()
    db_manager.close()
    logger.info("SentinelAI Backend stopped.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Firewall Attack Detection System for Computer Networks",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Proxy Headers for Cloud & Reverse Proxy Deployments (HTTPS forwarding)
try:
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
except Exception:
    pass

# CORS Configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [str(settings.CORS_ORIGINS)]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(ProtectedTargetError)
async def protected_target_exception_handler(request: Request, exc: ProtectedTargetError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(SentinelAIException)
async def sentinelai_exception_handler(request: Request, exc: SentinelAIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "An internal server error occurred.", "detail": "Internal error"},
    )


# Root Health Check routes for compatibility
app.include_router(health_endpoint.router, prefix="/health", tags=["health-root"])

# Mount Version 1 API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }
