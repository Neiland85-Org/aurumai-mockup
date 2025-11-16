"""
Main FastAPI application for AurumAI.
Initializes the application, includes routers, and sets up middleware and error handling.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.exception_handlers import (
    ErrorLoggingMiddleware,
    RequestIDMiddleware,
    application_error_handler,
    general_exception_handler,
    validation_error_handler,
)

# TEMPORARY: Use mock routers for development without database
from api.routers import esg_mock, ingest, machines_mock, predict_mock
from infrastructure.config.settings import settings
from infrastructure.logging import setup_logging
from infrastructure.metrics import get_metrics, system_info
from infrastructure.rate_limiting import limiter
from infrastructure.tracing import instrument_fastapi, setup_tracing
from models_errors import ApplicationError

# from api.routers import ingest_simple, machines_simple, predict_simple, esg_simple
# from infrastructure.db.postgres_config import init_database

# Configure structured logging (initialized once)
logger = setup_logging(
    level=settings.log_level,
    environment=settings.environment,
)

logger.info(
    "Initializing AurumAI Backend",
    extra={
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
    },
)

# Configure distributed tracing (if enabled)
if settings.tracing_enabled:
    logger.info(
        "Configuring OpenTelemetry tracing",
        extra={"otlp_endpoint": settings.tracing_otlp_endpoint or "console"},
    )
    setup_tracing(
        service_name=settings.tracing_service_name,
        service_version=settings.app_version,
        environment=settings.environment,
        otlp_endpoint=settings.tracing_otlp_endpoint or None,
        console_export=settings.tracing_console_export,
    )

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for AurumAI using Hexagonal Architecture with full observability.",
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Instrument FastAPI with OpenTelemetry (if enabled)
if settings.tracing_enabled:
    instrument_fastapi(app)
    logger.info("FastAPI instrumented with OpenTelemetry")

# Add middleware in correct order (LIFO):
# 1. Error logging (outermost)
# 2. Request ID (adds tracing)
# 3. CORS (FastAPI handles)
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
# TEMPORARY: Use mock endpoints (no database required)
app.include_router(machines_mock.router, prefix="/machines", tags=["Machines"])
app.include_router(predict_mock.router, prefix="/predict", tags=["Prediction"])
app.include_router(esg_mock.router, prefix="/esg", tags=["ESG"])
# Real routers (require database):
# app.include_router(machines.router, prefix="/machines", tags=["Machines"])
# app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
# app.include_router(esg.router, prefix="/esg", tags=["ESG"])


# Database initialization on startup
@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup event.
    Initializes the database connection and tables.
    """
    logger.info("Starting AurumAI Backend...")

    # Set system info metrics
    system_info.labels(
        version=settings.app_version,
        environment=settings.environment,
    ).set(1)

    # TODO: Initialize database when ready
    # await init_database()

    logger.info(
        "AurumAI Backend started successfully",
        extra={
            "prometheus_enabled": settings.prometheus_enabled,
            "tracing_enabled": settings.tracing_enabled,
        },
    )


# Root endpoint for health check
@app.get("/", tags=["Health"])
def read_root() -> dict[str, str]:
    """
    Root endpoint providing basic application information.
    """
    return {
        "status": "ok",
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# Prometheus metrics endpoint
@app.get("/metrics", include_in_schema=False, tags=["Monitoring"])
async def metrics() -> PlainTextResponse:
    """
    Prometheus metrics endpoint.

    Exposes application metrics in Prometheus text format for scraping.
    Includes HTTP request metrics, database metrics, ML prediction metrics,
    circuit breaker states, retry attempts, and error rates.

    Returns:
        PlainTextResponse: Metrics in Prometheus text format
    """
    return PlainTextResponse(get_metrics(), media_type="text/plain; version=0.0.4")


# Health check endpoint with detailed status
@app.get("/health", tags=["Health"])
def health_check() -> dict[str, Any]:
    """
    Detailed health check endpoint.

    Returns application health status and configuration.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "features": {
            "predictive": settings.feature_predictive,
            "carbon": settings.feature_carbon,
            "energy": settings.feature_energy,
            "water": settings.feature_water,
            "analytics": settings.feature_analytics,
        },
        "observability": {
            "logging": settings.log_format,
            "tracing_enabled": settings.tracing_enabled,
            "prometheus_enabled": settings.prometheus_enabled,
        },
    }
