from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from api import risks, controls, compliance, vendors, evidence, integrations, dashboard
from database import engine, Base
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    logger.info("Starting GRC Command Center...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down GRC Command Center...")


app = FastAPI(
    title="GRC Command Center",
    description="Governance, Risk & Compliance Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Include routers
app.include_router(risks.router, prefix="/api/risks", tags=["Risk Register"])
app.include_router(controls.router, prefix="/api/controls", tags=["Control Library"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["Vendor Risk"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    return {
        "message": "GRC Command Center API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )