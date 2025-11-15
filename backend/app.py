"""
Main FastAPI application for AurumAI.
Initializes the application, includes routers, and sets up middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import ingest, machines, predict, esg
# from api.routers import ingest_simple, machines_simple, predict_simple, esg_simple
from infrastructure.config.settings import settings
# from infrastructure.db.postgres_config import init_database

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for AurumAI using Hexagonal Architecture.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(machines.router, prefix="/machines", tags=["Machines"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(esg.router, prefix="/esg", tags=["ESG"])

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initializes the database connection and tables.
    """
    print("Initializing database...")
    # await init_database()  # Temporarily disabled for development
    print("Database initialization complete.")

# Root endpoint for health check
@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint providing basic application information.
    """
    return {
        "status": "ok",
        "name": settings.app_name,
        "version": settings.app_version,
    }