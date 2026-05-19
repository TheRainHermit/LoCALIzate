"""
LoCALIzate / CaliGuia Backend - Intelligent Tourist Guide for Cali, Colombia
=============================================================================

A comprehensive backend API for the LoCALIzate tourist guide application.
Provides endpoints for places, events, routes, chat assistant, AR features,
and user management with Supabase integration.

Modules:
    - core: Configuration, database, dependencies, and exceptions
    - models: SQLAlchemy/PostgREST models for database tables
    - repositories: Data access layer with CRUD operations
    - services: Business logic (AR, AI assistant, routing, geocoding)
    - routers: API endpoints organized by resource
    - schemas: Pydantic models for request/response validation
    - middleware: Custom middleware (auth, logging, rate limiting)
    - utils: Helper functions, validators, cache, logging

Version: 1.0.0
Author: LoCALIzate / CaliGuia Team
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import core modules
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.exceptions import handle_exception
from app.core.dependencies import check_rate_limit

# Import routers
from app.routers import (
    lugares_router,
    eventos_router,
    rutas_router,
    usuarios_router,
    chat_router,
    ar_router,
    analytics_router,
    websocket_router
)

# Import middleware
from app.middleware import (
    AuthMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# =====================================================
# APPLICATION FACTORY
# =====================================================

def create_app() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.APP_NAME,
        description="API para la guía turística inteligente de Cali, Colombia",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else "/docs",
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        debug=settings.DEBUG
    )
    
    # =====================================================
    # MIDDLEWARE (Order matters!)
    # =====================================================
    
    # 1. Logging middleware (first to log all requests)
    if settings.is_development:
        app.add_middleware(LoggingMiddleware)
    
    # 2. Rate limiting middleware
    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)
    
    # 3. CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # 4. Auth middleware (last to process authentication)
    # Commented by default - uncomment if you want global auth
    # app.add_middleware(AuthMiddleware)
    
    # =====================================================
    # EXCEPTION HANDLERS
    # =====================================================
    
    app.add_exception_handler(Exception, handle_exception)
    
    # =====================================================
    # LIFESPAN EVENTS
    # =====================================================
    
    @app.on_event("startup")
    async def startup_event():
        """Execute on application startup."""
        logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info(f"📁 Environment: {settings.APP_ENV}")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        
        # Initialize database connection
        db_ok = await init_db()
        if not db_ok:
            logger.warning("⚠️ Database connection failed - some features may not work")
        else:
            logger.info("✅ Database connection established")
        
        # Log registered routers
        logger.info("📋 Registered routers:")
        for route in app.routes:
            if hasattr(route, "methods"):
                logger.debug(f"   {route.methods} {route.path}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Execute on application shutdown."""
        logger.info(f"🛑 Shutting down {settings.APP_NAME}")
        await close_db()
        logger.info("✅ Clean shutdown complete")
    
    # =====================================================
    # HEALTH CHECK ENDPOINTS
    # =====================================================
    
    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "status": "operational",
            "docs": "/docs",
            "api_prefix": settings.API_PREFIX
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring."""
        from app.core.database import check_connection
        
        db_status = check_connection()
        
        return {
            "status": "healthy" if db_status["status"] == "connected" else "degraded",
            "timestamp": datetime.now().isoformat(),  # ← CORREGIDO: fecha dinámica
            "services": {
                "database": db_status,
                "api": "operational"
            },
            "environment": settings.APP_ENV,
            "version": settings.APP_VERSION
        }
    
    @app.get("/ready", tags=["Health"])
    async def readiness_check():
        """Readiness probe for Kubernetes/container orchestration."""
        from app.core.database import check_connection
        
        db_status = check_connection()
        
        if db_status["status"] != "connected":
            return {"ready": False, "reason": "database not connected"}
        
        return {"ready": True}
    
    @app.get("/version", tags=["Health"])
    async def version_info():
        """Version information endpoint."""
        return {
            "version": settings.APP_VERSION,
            "name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "api_prefix": settings.API_PREFIX
        }
    
    # =====================================================
    # REGISTER ROUTERS
    # =====================================================
    
    api_prefix = settings.API_PREFIX
    
    # Public routers
    app.include_router(lugares_router, prefix=api_prefix, tags=["Lugares"])
    app.include_router(eventos_router, prefix=api_prefix, tags=["Eventos"])
    
    # Protected routers (require authentication)
    app.include_router(usuarios_router, prefix=api_prefix, tags=["Usuarios"])
    app.include_router(rutas_router, prefix=api_prefix, tags=["Rutas"])
    app.include_router(chat_router, prefix=api_prefix, tags=["Chat"])
    
    # Feature routers
    app.include_router(ar_router, prefix=api_prefix, tags=["Realidad Aumentada"])
    app.include_router(analytics_router, prefix=api_prefix, tags=["Analytics"])
    
    # WebSocket router (different protocol)
    app.include_router(websocket_router, tags=["WebSocket"])
    
    # Log registered routes count
    route_count = len([route for route in app.routes if hasattr(route, "methods")])
    logger.info(f"✅ Registered {route_count} API routes")
    
    return app


# =====================================================
# CREATE APP INSTANCE
# =====================================================

# Singleton app instance
app = create_app()


# =====================================================
# MODULE EXPORTS
# =====================================================

__all__ = [
    "app",
    "create_app",
    "settings",
    "logger"
]


# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    """
    Run the application directly (for development).
    For production, use: uvicorn app:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    logger.info(f"Server will run on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"API docs available at http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 50)
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if settings.is_production else 1,
        log_level=settings.LOG_LEVEL.lower()
    )