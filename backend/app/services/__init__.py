"""
Servicios de lógica de negocio para LoCALIzate / CaliGuia Backend
=================================================================

Contiene la lógica de negocio y servicios auxiliares:
- Optimización de rutas (algoritmo del vecino más cercano)
- Asistente IA para chat turístico
- Geocodificación con OpenStreetMap (gratuito)
- Realidad Aumentada (AR) para ubicación de lugares
- Sistema de recomendaciones personalizadas
"""

# Optimizador de rutas
from app.services.optimizador_rutas import (
    optimizar_ruta,
    calcular_distancia_haversine,
    calcular_tiempo_estimado,
    obtener_instrucciones_simples
)

# Asistente IA
from app.services.asistente_ia import AsistenteLoCALIzate, asistente

# Geocodificación (solo OSM - gratuito, sin Google)
from app.services.geocoding_osm import GeocodingOSM, geocoding_osm

# Realidad Aumentada
from app.services.ar_service import ARService, ar_service, LugarAR

# Sistema de recomendaciones
from app.services.recommendation import (
    RecommendationService,
    recommendation_service,
    recomendar_lugares_por_interes,
    recomendar_lugares_similares,
    get_lugares_populares,
    get_lugares_tendencia
)

__all__ = [
    # Optimizador de rutas
    'optimizar_ruta',
    'calcular_distancia_haversine',
    'calcular_tiempo_estimado',
    'obtener_instrucciones_simples',
    
    # Asistente IA
    'asistente',
    'AsistenteLoCALIzate',
    
    # Geocodificación OSM
    'geocoding_osm',
    'GeocodingOSM',
    
    # Realidad Aumentada
    'ar_service',
    'ARService',
    'LugarAR',
    
    # Sistema de recomendaciones
    'RecommendationService',
    'recommendation_service',
    'recomendar_lugares_por_interes',
    'recomendar_lugares_similares',
    'get_lugares_populares',
    'get_lugares_tendencia',
]

# Versión del módulo
__version__ = "2.0.0"

# Descripción de servicios
SERVICE_DESCRIPTIONS = {
    "optimizador_rutas": "Optimización de rutas usando algoritmo del vecino más cercano",
    "asistente_ia": "Chatbot turístico para consultas sobre Cali",
    "geocoding_osm": "Geocodificación gratuita con OpenStreetMap Nominatim",
    "ar_service": "Realidad Aumentada para ubicar lugares en cámara",
    "recommendation": "Sistema de recomendaciones personalizadas por intereses"
}


def get_service_info() -> dict:
    """Obtener información de todos los servicios disponibles."""
    return {
        "version": __version__,
        "servicios": SERVICE_DESCRIPTIONS,
        "total_servicios": len(SERVICE_DESCRIPTIONS)
    }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Servicios de LoCALIzate / CaliGuia Backend")
    print("=" * 50)
    print(f"Versión: {__version__}")
    print(f"\nServicios disponibles:")
    for name, desc in SERVICE_DESCRIPTIONS.items():
        print(f"  ✓ {name}: {desc}")
    print("\n✅ Módulo de servicios cargado correctamente")