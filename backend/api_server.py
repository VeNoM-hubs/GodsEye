"""
FastAPI Server for GodsEye Honeypot Webhook
Provides webhook endpoints for receiving honeypot events from ESP32
"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.db_storage import GodsEyeDatabase
from backend.honeypot_api import create_honeypot_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="GodsEye Honeypot API",
        description="Webhook API for receiving events from ESP32 honeypot",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for honeypot POSTs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    db = GodsEyeDatabase()
    logger.info("✅ Database connected")
    
    # Include honeypot router
    honeypot_router = create_honeypot_router(db)
    app.include_router(honeypot_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Check API health status"""
        return {
            "status": "healthy",
            "service": "GodsEye Honeypot Webhook API",
            "database": "connected"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """API root - shows available endpoints"""
        return {
            "service": "GodsEye Honeypot Webhook API",
            "version": "1.0.0",
            "endpoints": {
                "POST /honeypot/log": "Submit honeypot event",
                "GET /honeypot/logs": "Retrieve all honeypot logs",
                "GET /honeypot/logs/{honeypot_id}": "Get logs for specific honeypot",
                "GET /honeypot/stats": "Get honeypot statistics",
                "DELETE /honeypot/logs/{log_id}": "Delete specific log",
                "GET /health": "Health check",
                "GET /docs": "API documentation (Swagger UI)",
                "GET /redoc": "API documentation (ReDoc)"
            }
        }
    
    return app


if __name__ == "__main__":
    app = create_app()
    
    # Run server
    logger.info("🚀 Starting GodsEye Honeypot API Server")
    logger.info("📍 Listening on http://0.0.0.0:8000")
    logger.info("📖 Swagger UI: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
