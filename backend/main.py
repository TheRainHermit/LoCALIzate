"""
LoCALIzate / CaliGuia Backend - Main Application
=================================================

API principal para la guía turística inteligente de Cali, Colombia.

Características:
    - Gestión de lugares turísticos
    - Eventos y festivales
    - Optimización de rutas
    - Asistente virtual IA
    - Realidad Aumentada (AR)
    - Perfiles de usuario y favoritos
    - Analytics y estadísticas
    - WebSockets para tiempo real

Endpoints:
    - /api/v1/lugares - Lugares turísticos
    - /api/v1/eventos - Eventos y festivales
    - /api/v1/rutas - Optimización y gestión de rutas
    - /api/v1/chat - Asistente virtual
    - /api/v1/usuarios - Perfiles y preferencias
    - /api/v1/ar - Realidad Aumentada
    - /api/v1/analytics - Estadísticas
    - /ws - WebSockets

Environment:
    Ver .env.example para variables requeridas
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# Importar routers
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

# Importar middlewares
from app.middleware import LoggingMiddleware, RateLimitMiddleware

# Importar core
from app.core.config import settings
from app.core.database import init_db, close_db, check_connection


# =====================================================
# LIFESPAN EVENTS
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación."""
    # Startup
    logger.info("=" * 50)
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📁 Entorno: {settings.APP_ENV}")
    logger.info(f"🔧 Modo debug: {settings.DEBUG}")
    logger.info(f"🌐 Servidor: {settings.HOST}:{settings.PORT}")
    logger.info("=" * 50)
    
    # Inicializar conexión a base de datos
    db_ok = await init_db()
    if not db_ok:
        logger.warning("⚠️ Advertencia: Conexión a Supabase falló")
    else:
        logger.info("✅ Conexión a Supabase establecida")
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info(f"🛑 Cerrando {settings.APP_NAME}")
    await close_db()
    logger.info("✅ Cierre completado")
    logger.info("=" * 50)


# =====================================================
# CREATE APP
# =====================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="API para la guía turística inteligente de Cali, Colombia",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.is_development else "/docs",
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    debug=settings.DEBUG,
    lifespan=lifespan
)


# =====================================================
# MIDDLEWARE (Order matters!)
# =====================================================

# 1. Logging middleware
app.add_middleware(LoggingMiddleware, log_headers=settings.is_development)

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


# =====================================================
# INCLUIR ROUTERS
# =====================================================

api_prefix = settings.API_PREFIX

app.include_router(lugares_router, prefix=api_prefix, tags=["Lugares Turísticos"])
app.include_router(eventos_router, prefix=api_prefix, tags=["Eventos"])
app.include_router(analytics_router, prefix=api_prefix, tags=["Analytics"])
app.include_router(chat_router, prefix=api_prefix, tags=["Chat - Asistente IA"])
app.include_router(ar_router, prefix=api_prefix, tags=["Realidad Aumentada"])
app.include_router(usuarios_router, prefix=api_prefix, tags=["Usuarios"])
app.include_router(rutas_router, prefix=api_prefix, tags=["Rutas"])
app.include_router(websocket_router, tags=["WebSocket"])

total_routes = len([route for route in app.routes if hasattr(route, "methods")])
logger.info(f"📡 {total_routes} endpoints registrados")


# =====================================================
# ENDPOINTS PÚBLICOS
# =====================================================

@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Guía turística inteligente de Cali, Colombia",
        "status": "operational",
        "environment": settings.APP_ENV,
        "docs_url": "/docs",
        "api_prefix": settings.API_PREFIX,
        "endpoints": {
            "lugares": f"{settings.API_PREFIX}/lugares",
            "eventos": f"{settings.API_PREFIX}/eventos",
            "rutas": f"{settings.API_PREFIX}/rutas/optimizar",
            "chat": f"{settings.API_PREFIX}/chat/mensaje",
            "ar": f"{settings.API_PREFIX}/ar/cercanos",
            "usuarios": f"{settings.API_PREFIX}/usuarios/perfil",
            "analytics": f"{settings.API_PREFIX}/analytics/globales",
            "websocket": "/ws/{client_id}",
            "vision": f"{settings.API_PREFIX}/vision/detect"
        },
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint para monitoreo."""
    db_status = check_connection()
    
    return {
        "status": "healthy" if db_status["status"] == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": db_status
        },
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION
    }


@app.get("/ready")
async def readiness_check():
    """Readiness probe."""
    db_status = check_connection()
    return {"ready": db_status["status"] == "connected"}


@app.get("/version")
async def version_info():
    """Información de versión."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "api_prefix": settings.API_PREFIX
    }


@app.get("/verify")
async def verify_system():
    """Verificar estado completo del sistema."""
    db_status = check_connection()
    
    stats = {}
    try:
        from app.database.supabase_client import supabase_client
        client = supabase_client.get_client()
        
        lugares = client.table("lugares").select("id", count="exact").limit(0).execute()
        stats["lugares"] = getattr(lugares, 'count', 0)
        
        eventos = client.table("eventos").select("id", count="exact").limit(0).execute()
        stats["eventos"] = getattr(eventos, 'count', 0)
        
        usuarios = client.table("usuarios").select("id", count="exact").limit(0).execute()
        stats["usuarios"] = getattr(usuarios, 'count', 0)
        
    except Exception as e:
        stats["error"] = str(e)
    
    return {
        "status": "running",
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "stats": stats
    }


# =====================================================
# MANEJADORES DE ERRORES
# =====================================================

from app.core.exceptions import handle_exception

app.add_exception_handler(Exception, handle_exception)


# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 50)
    logger.info(f"🚀 Iniciando servidor {settings.APP_NAME}")
    logger.info(f"📍 http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 Documentación: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if settings.is_production else 1,
        log_level=settings.LOG_LEVEL.lower()
    )