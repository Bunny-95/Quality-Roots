"""
Organic Roots Main Application
FastAPI application entry point with all routes and middleware
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager

from config import APP_NAME, VERSION, DEBUG, ALLOWED_ORIGINS, API_PREFIX, QR_CODES_DIR
from database import create_tables
from utils.seed_data import run_seed

# Import all routers
from routes.auth import router as auth_router
from routes.farmer import router as farmer_router
from routes.admin import router as admin_router
from routes.consumer import router as consumer_router
from routes.blockchain_routes import router as blockchain_router
from routes.ai_routes import router as ai_router
from routes.supply_chain import router as supply_chain_router
from blockchain.chain import blockchain_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🌿 Starting {APP_NAME} v{VERSION}...")
    
    # Create database tables
    create_tables()
    print("✅ Database tables created/verified")
    
    # Initialize blockchain (create genesis block)
    blockchain_manager.init()
    print("✅ Blockchain initialized")
    
    # Run seed data if database is empty
    run_seed()
    print("✅ Seed data initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="AI-enabled, simulated-blockchain-based smart agricultural supply chain provenance system",
    debug=DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for QR codes
if QR_CODES_DIR.exists():
    app.mount("/qr_codes", StaticFiles(directory=str(QR_CODES_DIR)), name="qr_codes")

# Include all routers with API prefix
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(farmer_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(consumer_router, prefix=API_PREFIX)
app.include_router(blockchain_router, prefix=API_PREFIX)
app.include_router(ai_router, prefix=API_PREFIX)
app.include_router(supply_chain_router, prefix=API_PREFIX)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": APP_NAME,
        "version": VERSION,
        "description": "AI-enabled agricultural supply chain provenance system",
        "docs_url": "/docs",
        "api_prefix": API_PREFIX,
        "endpoints": {
            "auth": f"{API_PREFIX}/auth",
            "farmer": f"{API_PREFIX}/farmer",
            "admin": f"{API_PREFIX}/admin",
            "consumer": f"{API_PREFIX}/consumer",
            "blockchain": f"{API_PREFIX}/blockchain",
            "ai": f"{API_PREFIX}/ai",
            "supply_chain": f"{API_PREFIX}/supply"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": VERSION,
        "debug": DEBUG
    }

# QR code serving endpoint
@app.get("/qr/{batch_code}")
async def get_qr_code(batch_code: str):
    """Serve QR code image for a batch"""
    from utils.qr_generator import qr_generator
    
    # Get QR code info
    qr_info = qr_generator.get_qr_code_info(batch_code)
    
    if not qr_info:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Serve the file
    qr_path = qr_info["filepath"]
    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="QR code file not found")

# API documentation endpoints
@app.get("/api")
async def api_info():
    """API information and available endpoints"""
    return {
        "title": APP_NAME,
        "version": VERSION,
        "api_prefix": API_PREFIX,
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "available_routes": [
            {
                "name": "Authentication",
                "prefix": f"{API_PREFIX}/auth",
                "description": "User registration, login, and profile management"
            },
            {
                "name": "Farmer",
                "prefix": f"{API_PREFIX}/farmer",
                "description": "Farmer-specific functionality for products and batches"
            },
            {
                "name": "Admin",
                "prefix": f"{API_PREFIX}/admin",
                "description": "Administrative functions and system oversight"
            },
            {
                "name": "Consumer",
                "prefix": f"{API_PREFIX}/consumer",
                "description": "Public product verification and journey tracking"
            },
            {
                "name": "Blockchain",
                "prefix": f"{API_PREFIX}/blockchain",
                "description": "Blockchain operations and verification"
            },
            {
                "name": "AI Services",
                "prefix": f"{API_PREFIX}/ai",
                "description": "AI-powered quality grading, fraud detection, and forecasting"
            },
            {
                "name": "Supply Chain",
                "prefix": f"{API_PREFIX}/supply",
                "description": "Supply chain event management and tracking"
            }
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": "Not Found",
        "message": f"Endpoint {request.url.path} not found",
        "available_docs": "/docs"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "debug": DEBUG
    }

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    """Handle validation errors"""
    return {
        "error": "Validation Error",
        "message": "Invalid input data",
        "details": exc.detail()
    }

# Startup confirmation
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print(f"🚀 {APP_NAME} API is ready!")
    print(f"   📚 API Documentation: http://localhost:8000/docs")
    print(f"   🔗 API Base URL: http://localhost:8000{API_PREFIX}")
    print(f"   🌱 QR Codes: http://localhost:8000/qr_codes")
    print(f"   ❤️  Health Check: http://localhost:8000/health")

if __name__ == "__main__":
    import uvicorn
    
    print(f"🌿 Starting {APP_NAME} development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
