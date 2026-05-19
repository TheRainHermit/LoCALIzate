"""
Routers module for LoCALIzate / CaliGuia Backend
=================================================

API endpoints organized by resource.
All routers are registered in this module and exported for use in main.py.

Available Routers:
    - lugares_router: CRUD operations for tourist places
    - eventos_router: CRUD operations for events and festivals
    - rutas_router: Route optimization and user itineraries
    - usuarios_router: User profiles and preferences
    - chat_router: AI assistant chat endpoints
    - ar_router: Augmented Reality features
    - analytics_router: Usage analytics and statistics
    - websocket_router: WebSocket connections for real-time features

Usage in main.py:
    from app.routers import (
        lugares_router, eventos_router, rutas_router,
        usuarios_router, chat_router, ar_router,
        analytics_router, websocket_router
    )
    
    app.include_router(lugares_router, prefix="/api/v1", tags=["Lugares"])
"""

# Core routers
from app.routers.lugares import router as lugares_router
from app.routers.eventos import router as eventos_router
from app.routers.rutas import router as rutas_router
from app.routers.usuarios import router as usuarios_router

# Feature routers
from app.routers.chat import router as chat_router
from app.routers.ar import router as ar_router
from app.routers.analytics import router as analytics_router
from app.routers.websocket import router as websocket_router

# Optional: Health check router (puedes agregarlo si lo necesitas)
# from app.routers.health import router as health_router

__all__ = [
    # Core routers
    "lugares_router",
    "eventos_router",
    "rutas_router",
    "usuarios_router",
    
    # Feature routers
    "chat_router",
    "ar_router",
    "analytics_router",
    "websocket_router",
]

# Versión del módulo
__version__ = "1.0.0"

# Descripción de routers
ROUTER_DESCRIPTIONS = {
    "lugares_router": "Endpoints para lugares turísticos (CRUD, búsqueda, filtros)",
    "eventos_router": "Endpoints para eventos y festivales en Cali",
    "rutas_router": "Optimización de rutas e itinerarios de usuario",
    "usuarios_router": "Gestión de perfiles y preferencias de usuario",
    "chat_router": "Asistente virtual IA para consultas turísticas",
    "ar_router": "Realidad Aumentada para ubicar lugares en cámara",
    "analytics_router": "Estadísticas y analytics de uso",
    "websocket_router": "Conexiones WebSocket para chat y ubicación en tiempo real"
}


def get_router_info() -> dict:
    """Obtener información de todos los routers disponibles."""
    return {
        "version": __version__,
        "routers": ROUTER_DESCRIPTIONS,
        "total_routers": len(ROUTER_DESCRIPTIONS)
    }


def list_routers() -> list:
    """Listar todos los nombres de routers disponibles."""
    return list(ROUTER_DESCRIPTIONS.keys())


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Routers Module - Información")
    print("=" * 50)
    
    info = get_router_info()
    print(f"\n📦 Versión: {info['version']}")
    print(f"📋 Total routers: {info['total_routers']}")
    print("\n📡 Routers disponibles:")
    
    for name, description in info['routers'].items():
        print(f"   ✓ {name}: {description}")
    
    print("\n✅ Módulo de routers cargado correctamente")