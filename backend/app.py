from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import ingest, predict, esg, machines
from infrastructure.db.database import init_db

app = FastAPI(
    title="AurumAI Mockup Backend",
    description="Backend funcional para demo (Predictivo + ESG)",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()


# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(esg.router, prefix="/esg", tags=["esg"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])


@app.get("/", tags=["root"])
def root():
    return {"status": "ok", "service": "aurumai-backend", "version": "0.1.0"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy", "service": "aurumai-backend"}
