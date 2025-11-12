"""FastAPI application for BugBountyCrawler."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from .routers import scans, findings, programs, targets, users, metrics
from ..core.config import get_settings
from ..core.logger import setup_logging

# Setup logging
settings = get_settings()
setup_logging(settings)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BugBountyCrawler API",
    description="A production-ready, legal, modular BugBountyCrawler for ethical bug bounty hunting",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include routers
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])
app.include_router(findings.router, prefix="/api/findings", tags=["findings"])
app.include_router(programs.router, prefix="/api/programs", tags=["programs"])
app.include_router(targets.router, prefix="/api/targets", tags=["targets"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])

# Mount static files
app.mount("/static", StaticFiles(directory="bugbountycrawler/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="bugbountycrawler/web/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the metrics dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("BugBountyCrawler API starting up...")
    
    # Initialize database
    from ..database.connection import init_database
    init_database()
    
    logger.info("BugBountyCrawler API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("BugBountyCrawler API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

















