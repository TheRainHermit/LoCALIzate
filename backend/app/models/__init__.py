"""
Models module for LoCALIzate / CaliGuia Backend
================================================

Database models representing the core entities of the application.
These models map to Supabase/PostgreSQL tables and define the
structure of data used throughout the application.

Available Models:
    - Lugar: Tourist places in Cali (Cristo Rey, Gato del Río, etc.)
    - Evento: Events, festivals, and activities (Feria de Cali, etc.)
    - Usuario: User profiles and preferences
    - Ruta: User-created itineraries
    - Conversacion: Chat conversations with AI assistant
    - Mensaje: Individual messages in conversations
    - ARSession: Augmented reality session tracking
    - Favorito: User's favorite places
    - Resena: User reviews and ratings

Usage:
    from app.models import Lugar, Evento, Usuario
    
    # Use with Supabase
    lugar = Lugar(nombre="Cristo Rey", lat=3.43587, lng=-76.56490)
"""

from app.models.lugar import (
    Lugar,
    LugarCreate,
    LugarUpdate,
    LugarInDB,
    LugarWithRating,
    LugarFilters
)

from app.models.evento import (
    Evento,
    EventoCreate,
    EventoUpdate,
    EventoInDB,
    EventoFilters,
    EventoWithLugar
)

from app.models.usuario import (
    Usuario,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioInDB,
    UsuarioProfile,
    UsuarioIntereses
)

from app.models.ruta import (
    Ruta,
    RutaCreate,
    RutaUpdate,
    RutaInDB,
    RutaDetalle,
    RutaDetalleCreate,
    RutaWithDetalles,
    RutaOptimizada,
    RutaStep
)

from app.models.chat import (
    Conversacion,
    ConversacionCreate,
    ConversacionInDB,
    Mensaje,
    MensajeCreate,
    MensajeInDB,
    ChatRequest,
    ChatResponse,
    IntencionType
)

from app.models.ar import (
    ARSession,
    ARSessionCreate,
    ARSessionInDB,
    ARPointOfInterest,
    ARLocationData,
    ARObject,
    ARFilterType
)

# Re-export commonly used types
__all__ = [
    # Lugar models
    "Lugar",
    "LugarCreate",
    "LugarUpdate",
    "LugarInDB",
    "LugarWithRating",
    "LugarFilters",
    
    # Evento models
    "Evento",
    "EventoCreate",
    "EventoUpdate",
    "EventoInDB",
    "EventoFilters",
    "EventoWithLugar",
    
    # Usuario models
    "Usuario",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioInDB",
    "UsuarioProfile",
    "UsuarioIntereses",
    
    # Ruta models
    "Ruta",
    "RutaCreate",
    "RutaUpdate",
    "RutaInDB",
    "RutaDetalle",
    "RutaDetalleCreate",
    "RutaWithDetalles",
    "RutaOptimizada",
    "RutaStep",
    
    # Chat models
    "Conversacion",
    "ConversacionCreate",
    "ConversacionInDB",
    "Mensaje",
    "MensajeCreate",
    "MensajeInDB",
    "ChatRequest",
    "ChatResponse",
    "IntencionType",
    
    # AR models
    "ARSession",
    "ARSessionCreate",
    "ARSessionInDB",
    "ARPointOfInterest",
    "ARLocationData",
    "ARObject",
    "ARFilterType",
]

__version__ = "1.0.0"

# Module metadata
MODEL_DESCRIPTIONS = {
    "Lugar": "Lugares turísticos de Cali con coordenadas, horarios, precios y calificaciones",
    "Evento": "Eventos, festivales y actividades en Cali (Feria, Petronio, etc.)",
    "Usuario": "Perfiles de usuario con preferencias y configuración",
    "Ruta": "Itinerarios personalizados creados por usuarios",
    "Conversacion": "Historial de conversaciones con el asistente virtual",
    "Mensaje": "Mensajes individuales en conversaciones",
    "ARSession": "Sesiones de realidad aumentada para tracking",
    "Favorito": "Lugares marcados como favoritos por usuarios",
    "Resena": "Calificaciones y reseñas de usuarios"
}


def get_all_models() -> list:
    """Return list of all available model names."""
    return [
        "Lugar",
        "Evento", 
        "Usuario",
        "Ruta",
        "Conversacion",
        "Mensaje",
        "ARSession",
        "Favorito",
        "Resena"
    ]


def get_model_description(model_name: str) -> str:
    """Get description for a specific model."""
    return MODEL_DESCRIPTIONS.get(model_name, "Modelo no encontrado")


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("Models module loaded successfully")
    print(f"Available models: {', '.join(get_all_models())}")
    print("\nModel descriptions:")
    for model in get_all_models():
        print(f"  - {model}: {get_model_description(model)}")