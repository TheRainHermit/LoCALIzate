"""
Schemas module for LoCALIzate / CaliGuia Backend
=================================================

Pydantic models for request/response validation.
Provides type-safe data structures for all API endpoints.

Available Schemas:
    - lugar: Tourist place schemas (request/response)
    - evento: Event and festival schemas
    - usuario: User profile and preferences schemas
    - ruta: Route optimization and itinerary schemas
    - chat: Conversation and message schemas
    - ar: Augmented Reality schemas

Usage:
    from app.schemas import LugarResponse, LugarCreate, LugarUpdate
    from app.schemas import EventoResponse, EventoCreate
    from app.schemas import UsuarioResponse, UsuarioUpdate
"""

# Lugar schemas
from app.schemas.lugar import (
    LugarBase,
    LugarCreate,
    LugarUpdate,
    LugarResponse,
    LugarDetailResponse,
    LugarListResponse,
    LugarCercanoResponse,
    LugarFilters,
    InteresType,
    LugarWithRating,
    LugarProximityResponse
)

# Evento schemas
from app.schemas.evento import (
    EventoBase,
    EventoCreate,
    EventoUpdate,
    EventoResponse,
    EventoDetailResponse,
    EventoListResponse,
    EventoProximosResponse,
    EventoFilters,
    EventoFrecuencia,
    EventoWithLugar
)

# Usuario schemas
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioProfile,
    UsuarioPreferences,
    UsuarioPreferencesUpdate,
    UsuarioInteresesUpdate,
    UsuarioStatsResponse,
    FavoritoResponse,
    IdiomaType,
    TemaType,
    NotificacionType
)

# Ruta schemas
from app.schemas.ruta import (
    RutaBase,
    RutaCreate,
    RutaUpdate,
    RutaResponse,
    RutaDetailResponse,
    RutaListResponse,
    RutaOptimizarRequest,
    RutaOptimizadaResponse,
    RutaStepResponse,
    RutaGuardadaResponse,
    RutaTemplateResponse,
    ModoTransporte,
    DistanciaResponse
)

# Chat schemas
from app.schemas.chat import (
    MensajeBase,
    MensajeRequest,
    MensajeResponse,
    ChatResponse,
    ChatRequest,
    ConversacionResponse,
    ConversacionDetailResponse,
    MensajeHistorialResponse,
    SugerenciaResponse,
    RolMensaje,
    IntencionType
)

# AR schemas
from app.schemas.ar import (
    LugarARResponse,
    InstruccionARResponse,
    PuntoCardinalResponse,
    BrújulaARResponse,
    ARCercanosRequest,
    ARStatsResponse,
    ARFilterType,
    ARObjectType,
    ARTriggerType
)

__all__ = [
    # Lugar schemas
    "LugarBase",
    "LugarCreate",
    "LugarUpdate",
    "LugarResponse",
    "LugarDetailResponse",
    "LugarListResponse",
    "LugarCercanoResponse",
    "LugarFilters",
    "InteresType",
    "LugarWithRating",
    "LugarProximityResponse",
    
    # Evento schemas
    "EventoBase",
    "EventoCreate",
    "EventoUpdate",
    "EventoResponse",
    "EventoDetailResponse",
    "EventoListResponse",
    "EventoProximosResponse",
    "EventoFilters",
    "EventoFrecuencia",
    "EventoWithLugar",
    
    # Usuario schemas
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioProfile",
    "UsuarioPreferences",
    "UsuarioPreferencesUpdate",
    "UsuarioInteresesUpdate",
    "UsuarioStatsResponse",
    "FavoritoResponse",
    "IdiomaType",
    "TemaType",
    "NotificacionType",
    
    # Ruta schemas
    "RutaBase",
    "RutaCreate",
    "RutaUpdate",
    "RutaResponse",
    "RutaDetailResponse",
    "RutaListResponse",
    "RutaOptimizarRequest",
    "RutaOptimizadaResponse",
    "RutaStepResponse",
    "RutaGuardadaResponse",
    "RutaTemplateResponse",
    "ModoTransporte",
    "DistanciaResponse",
    
    # Chat schemas
    "MensajeBase",
    "MensajeRequest",
    "MensajeResponse",
    "ChatResponse",
    "ChatRequest",
    "ConversacionResponse",
    "ConversacionDetailResponse",
    "MensajeHistorialResponse",
    "SugerenciaResponse",
    "RolMensaje",
    "IntencionType",
    
    # AR schemas
    "LugarARResponse",
    "InstruccionARResponse",
    "PuntoCardinalResponse",
    "BrújulaARResponse",
    "ARCercanosRequest",
    "ARStatsResponse",
    "ARFilterType",
    "ARObjectType",
    "ARTriggerType",
]

__version__ = "1.0.0"

# Schema descriptions
SCHEMA_DESCRIPTIONS = {
    "lugar": "Esquemas para lugares turísticos (CRUD, filtros, respuestas)",
    "evento": "Esquemas para eventos y festivales",
    "usuario": "Esquemas para perfiles, preferencias y favoritos",
    "ruta": "Esquemas para optimización y gestión de rutas",
    "chat": "Esquemas para mensajes y conversaciones",
    "ar": "Esquemas para Realidad Aumentada"
}


def get_schema_info() -> dict:
    """Get information about available schemas."""
    return {
        "version": __version__,
        "schemas": SCHEMA_DESCRIPTIONS,
        "total_categories": len(SCHEMA_DESCRIPTIONS)
    }


def list_schemas() -> list:
    """List all schema categories."""
    return list(SCHEMA_DESCRIPTIONS.keys())


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Schemas Module - Information")
    print("=" * 50)
    
    info = get_schema_info()
    print(f"\n📦 Version: {info['version']}")
    print(f"📋 Total categories: {info['total_categories']}")
    print("\n📁 Schema categories available:")
    
    for name, description in info['schemas'].items():
        print(f"   ✓ {name}: {description}")
    
    print("\n✅ Schemas module loaded successfully")