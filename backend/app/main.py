from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine
from .routers import auth, logs, alerts, incidents, dashboard, threat_detection

# Create database tables on startup
from .models import Base
from .seed import seed_default_data
import asyncio

app = FastAPI(
    title="Mini SIEM & SOC API",
    description="A lightweight SIEM system with SOC monitoring capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(threat_detection.router, prefix="/api/threat-detection", tags=["Threat Detection"])

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed initial data
    await seed_default_data()

@app.get("/")
async def root():
    return {
        "message": "Mini SIEM & SOC Monitoring API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-09-09T12:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)