"""
Endpoints para Realidad Aumentada (AR) - LoCALIzate Backend
===========================================================

Proporciona endpoints para funcionalidades de Realidad Aumentada:
    - Lugares cercanos para mostrar en AR
    - Instrucciones visuales basadas en dirección de la cámara
    - Orientación de lugares por puntos cardinales (brújula AR)
    - Detección de lugares en el campo de visión

Dependencias:
    - ARService: Cálculos geométricos y filtrado de lugares
    - LugarRepository: Acceso a datos de lugares turísticos
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.services.ar_service import ar_service, ARService
from app.repositories.lugar_repo import LugarRepository
from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.core.exceptions import ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ar", tags=["Realidad Aumentada"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class LugarARResponse(BaseModel):
    """Respuesta para lugar en AR"""
    id: int
    nombre: str
    lat: float
    lng: float
    distancia_km: float
    distancia_formateada: str
    azimuth: float
    descripcion_corta: str
    rating: float
    icono: str
    horario: Optional[str] = None
    
    class Config:
        from_attributes = True


class InstruccionARResponse(BaseModel):
    """Respuesta con instrucción visual para AR"""
    id: int
    nombre: str
    icono: str
    distancia_km: float
    distancia_formateada: str
    direccion: str
    direccion_corta: str
    angulo_relativo: float
    azimuth: float
    descripcion: str
    rating: float
    rating_stars: str
    imagen_url: Optional[str] = None
    horario: Optional[str] = None


class PuntoCardinalResponse(BaseModel):
    """Respuesta para punto cardinal en brújula AR"""
    nombre: str
    distancia_km: float
    distancia_formateada: str
    azimuth: float


class BrújulaARResponse(BaseModel):
    """Respuesta completa para brújula AR"""
    N: List[PuntoCardinalResponse] = []
    NE: List[PuntoCardinalResponse] = []
    E: List[PuntoCardinalResponse] = []
    SE: List[PuntoCardinalResponse] = []
    S: List[PuntoCardinalResponse] = []
    SW: List[PuntoCardinalResponse] = []
    W: List[PuntoCardinalResponse] = []
    NW: List[PuntoCardinalResponse] = []
    
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    centro: Optional[Dict[str, float]] = None


class ARCercanosRequest(BaseModel):
    """Request para obtener lugares cercanos AR"""
    lat: float = Field(..., ge=-90, le=90, description="Latitud del usuario")
    lng: float = Field(..., ge=-180, le=180, description="Longitud del usuario")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección del teléfono en grados")
    radio_km: float = Field(2.0, ge=0.5, le=10, description="Radio de búsqueda en km")
    max_resultados: int = Field(20, ge=1, le=50, description="Máximo número de resultados")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _formatear_distancia(distancia_km: float) -> str:
    """Formatear distancia para mostrar al usuario."""
    if distancia_km < 0.1:
        return f"{int(distancia_km * 1000)} m"
    return f"{distancia_km:.1f} km"


def _calcular_rating_stars(rating: float) -> str:
    """Calcular representación visual del rating."""
    full = int(rating)
    half = rating - full >= 0.5
    empty = 5 - full - (1 if half else 0)
    return "★" * full + ("½" if half else "") + "☆" * empty


def _get_punto_cardinal(azimuth: float) -> str:
    """Convertir azimuth a punto cardinal de 8 direcciones."""
    if azimuth < 22.5:
        return "N"
    elif azimuth < 67.5:
        return "NE"
    elif azimuth < 112.5:
        return "E"
    elif azimuth < 157.5:
        return "SE"
    elif azimuth < 202.5:
        return "S"
    elif azimuth < 247.5:
        return "SW"
    elif azimuth < 292.5:
        return "W"
    elif azimuth < 337.5:
        return "NW"
    else:
        return "N"


# =====================================================
# ENDPOINTS
# =====================================================

@router.get("/cercanos", response_model=List[LugarARResponse])
async def obtener_lugares_cercanos_ar(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del usuario"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud del usuario"),
    heading: Optional[float] = Query(None, ge=0, le=360, description="Dirección del teléfono en grados"),
    radio_km: float = Query(2.0, ge=0.5, le=10, description="Radio de búsqueda en km"),
    max_resultados: int = Query(20, ge=1, le=50, description="Máximo número de resultados"),
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """
    Obtener lugares cercanos para mostrar en Realidad Aumentada.
    
    - Si se proporciona heading, solo devuelve lugares en el campo de visión
    - Si no hay heading, devuelve todos los lugares cercanos ordenados por distancia
    - Los resultados incluyen distancia, azimuth y metadata para overlay AR
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Obtener todos los lugares activos
        lugares_db = await lugar_repo.get_all_active(limit=100)
        
        if not lugares_db:
            return []
        
        # Configurar servicio AR con radio personalizado
        ar_svc = ARService(radio_busqueda_km=radio_km)
        
        # Calcular lugares cercanos y filtrar por heading si existe
        lugares_ar = ar_svc.lugares_cerca_para_ar(
            lat, lng, lugares_db, heading, max_resultados
        )
        
        return [
            LugarARResponse(
                id=l.id,
                nombre=l.nombre,
                lat=l.lat,
                lng=l.lng,
                distancia_km=l.distancia_km,
                distancia_formateada=l.distancia_formateada,
                azimuth=l.azimuth,
                descripcion_corta=l.descripcion_corta[:100] if l.descripcion_corta else "",
                rating=l.rating,
                icono=l.icono,
                horario=l.horario
            ) for l in lugares_ar
        ]
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en obtener_lugares_cercanos_ar: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/instruccion", response_model=Optional[InstruccionARResponse])
async def obtener_instruccion_ar(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del usuario"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud del usuario"),
    heading: float = Query(..., ge=0, le=360, description="Dirección del teléfono en grados"),
    radio_km: float = Query(2.0, ge=0.5, le=10, description="Radio de búsqueda en km"),
    supabase = Depends(get_db)
):
    """
    Obtener instrucción visual para el lugar más cercano en la dirección de la cámara.
    
    Útil para mostrar una sola tarjeta AR con la instrucción de hacia dónde girar.
    Retorna None si no hay lugares en la dirección actual.
    """
    try:
        lugar_repo = LugarRepository(supabase)
        lugares_db = await lugar_repo.get_all_active(limit=100)
        
        if not lugares_db:
            return None
        
        ar_svc = ARService(radio_busqueda_km=radio_km)
        
        # Filtrar lugares en la dirección de la cámara
        lugares_ar = ar_svc.lugares_cerca_para_ar(lat, lng, lugares_db, heading, max_resultados=5)
        
        if not lugares_ar:
            return None
        
        # El más cercano en la dirección de la cámara
        lugar_mas_cercano = lugares_ar[0]
        
        instruccion = ar_svc.generar_instruccion_ar(lugar_mas_cercano, heading)
        
        return InstruccionARResponse(
            id=lugar_mas_cercano.id,
            nombre=lugar_mas_cercano.nombre,
            icono=lugar_mas_cercano.icono,
            distancia_km=lugar_mas_cercano.distancia_km,
            distancia_formateada=lugar_mas_cercano.distancia_formateada,
            direccion=instruccion["direccion"],
            direccion_corta=instruccion["direccion_corta"],
            angulo_relativo=instruccion["angulo_relativo"],
            azimuth=lugar_mas_cercano.azimuth,
            descripcion=instruccion["descripcion"],
            rating=lugar_mas_cercano.rating,
            rating_stars=_calcular_rating_stars(lugar_mas_cercano.rating),
            imagen_url=lugar_mas_cercano.imagen_url,
            horario=lugar_mas_cercano.horario
        )
        
    except Exception as e:
        logger.error(f"Error en obtener_instruccion_ar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compass", response_model=BrújulaARResponse)
async def obtener_orientacion_puntos_cardinales(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del usuario"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud del usuario"),
    radio_km: float = Query(5.0, ge=1, le=20, description="Radio de búsqueda en km"),
    supabase = Depends(get_db)
):
    """
    Obtener orientación de lugares organizada por puntos cardinales.
    
    Útil para implementar una brújula AR que muestre en qué dirección
    se encuentran los diferentes lugares turísticos.
    
    Retorna un objeto con 8 direcciones (N, NE, E, SE, S, SW, W, NW)
    cada una con la lista de lugares en esa dirección.
    """
    try:
        lugar_repo = LugarRepository(supabase)
        lugares_db = await lugar_repo.get_all_active(limit=100)
        
        if not lugares_db:
            return BrújulaARResponse(centro={"lat": lat, "lng": lng})
        
        ar_svc = ARService(radio_busqueda_km=radio_km)
        
        # Inicializar estructura de respuesta
        resultado = BrújulaARResponse(centro={"lat": lat, "lng": lng})
        
        for lugar in lugares_db:
            # Extraer coordenadas
            lugar_lat = lugar.get('lat', lugar.get('latitud', 0))
            lugar_lng = lugar.get('lng', lugar.get('longitud', 0))
            
            # Calcular azimuth y distancia
            azimuth = ar_svc.calcular_azimuth(lat, lng, lugar_lat, lugar_lng)
            distancia = ar_svc.calcular_distancia_haversine(lat, lng, lugar_lat, lugar_lng)
            
            # Filtrar por radio
            if distancia > radio_km:
                continue
            
            # Determinar punto cardinal
            direccion = _get_punto_cardinal(azimuth)
            
            punto = PuntoCardinalResponse(
                nombre=lugar.get('nombre', 'Lugar sin nombre'),
                distancia_km=round(distancia, 2),
                distancia_formateada=_formatear_distancia(distancia),
                azimuth=round(azimuth, 1)
            )
            
            # Agregar a la dirección correspondiente
            getattr(resultado, direccion).append(punto)
        
        # Ordenar cada lista por distancia
        for direccion in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            lista = getattr(resultado, direccion)
            lista.sort(key=lambda x: x.distancia_km)
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en obtener_orientacion_puntos_cardinales: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cercanos", response_model=List[LugarARResponse])
async def obtener_lugares_cercanos_ar_post(
    request: ARCercanosRequest,
    supabase = Depends(get_db)
):
    """
    Versión POST de obtener lugares cercanos para AR.
    Útil cuando se envían muchos parámetros o desde dispositivos móviles.
    """
    return await obtener_lugares_cercanos_ar(
        lat=request.lat,
        lng=request.lng,
        heading=request.heading,
        radio_km=request.radio_km,
        max_resultados=request.max_resultados,
        supabase=supabase
    )


@router.get("/estadisticas")
async def obtener_estadisticas_ar(
    lat: float = Query(..., description="Latitud del usuario"),
    lng: float = Query(..., description="Longitud del usuario"),
    radio_km: float = Query(2.0, description="Radio de búsqueda en km"),
    supabase = Depends(get_db)
):
    """
    Obtener estadísticas de lugares cercanos para AR.
    
    Retorna métricas como:
    - Total de lugares cercanos
    - Cantidad por interés
    - Lugar más cercano
    - Distribución por distancia
    """
    try:
        lugar_repo = LugarRepository(supabase)
        lugares_db = await lugar_repo.get_all_active(limit=100)
        
        ar_svc = ARService(radio_busqueda_km=radio_km)
        
        estadisticas = ar_svc.get_estadisticas_cercania(lat, lng, lugares_db)
        
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error en obtener_estadisticas_ar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_ar_info():
    """Obtener información sobre el servicio AR."""
    return {
        "servicio": "Realidad Aumentada - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para visualización AR de lugares turísticos",
        "endpoints_disponibles": [
            "GET /ar/cercanos",
            "GET /ar/instruccion",
            "GET /ar/compass",
            "POST /ar/cercanos",
            "GET /ar/estadisticas",
            "GET /ar/info"
        ],
        "configuracion": {
            "radio_busqueda_default_km": 2.0,
            "max_resultados_default": 20,
            "soporta_heading": True
        }
    }