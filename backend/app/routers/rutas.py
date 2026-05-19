"""
Endpoints para Rutas - LoCALIzate Backend
========================================

Proporciona endpoints para planificación y optimización de rutas turísticas:
    - Optimización de orden de visita (algoritmo vecino más cercano)
    - Cálculo de distancias y tiempos entre lugares
    - Guardado de rutas personalizadas por usuario
    - Listado y gestión de rutas guardadas
    - Plantillas de rutas predefinidas

Dependencias:
    - RutaRepository: Acceso a datos de rutas
    - LugarRepository: Acceso a datos de lugares
    - OptimizadorRutas: Algoritmo de optimización
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
import logging

from app.repositories.ruta_repo import RutaRepository
from app.repositories.lugar_repo import LugarRepository
from app.services.optimizador_rutas import (
    optimizar_ruta,
    optimizar_ruta_con_retorno,
    calcular_distancia_haversine,
    calcular_tiempo_estimado,
    obtener_instrucciones_completas,
    ModoTransporte
)
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, get_pagination, PaginationParams
from app.core.exceptions import NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rutas", tags=["Rutas"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class RutaOptimizarRequest(BaseModel):
    """Request para optimizar una ruta"""
    lugares_ids: List[int] = Field(..., min_length=1, max_length=15, description="IDs de lugares a visitar")
    origen_lat: float = Field(..., ge=-90, le=90, description="Latitud de origen")
    origen_lng: float = Field(..., ge=-180, le=180, description="Longitud de origen")
    modo: str = Field(default="walking", description="Modo de transporte: walking, biking, driving")
    retornar_origen: bool = Field(default=False, description="Si debe retornar al punto de inicio")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lugares_ids": [1, 2, 3],
                "origen_lat": 3.4516,
                "origen_lng": -76.5320,
                "modo": "walking",
                "retornar_origen": False
            }
        }


class PasoRutaResponse(BaseModel):
    """Paso individual de una ruta"""
    orden: int
    lugar_id: int
    nombre: str
    lat: float
    lng: float
    distancia_km: float
    distancia_formateada: str
    tiempo_min: int
    tiempo_formateado: str
    instruccion: str


class RutaOptimizadaResponse(BaseModel):
    """Respuesta de ruta optimizada"""
    lugares_ordenados: List[PasoRutaResponse]
    distancia_total_km: float
    tiempo_total_min: int
    tiempo_formateado: str
    cantidad_lugares: int
    modo_transporte: str
    modo_nombre: str
    advertencias: List[str] = []


class RutaGuardarRequest(BaseModel):
    """Request para guardar una ruta"""
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    lugares_ids: List[int] = Field(..., min_length=1, max_length=15)
    fecha_visita: Optional[date] = None
    hora_inicio: Optional[str] = None
    compartida: bool = Field(default=False)


class RutaGuardadaResponse(BaseModel):
    """Respuesta de ruta guardada"""
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_visita: Optional[str]
    hora_inicio: Optional[str]
    distancia_total_km: float
    tiempo_total_min: int
    tiempo_formateado: str
    cantidad_lugares: int
    completada: bool
    compartida: bool
    created_at: str


class RutaDetalleResponse(RutaGuardadaResponse):
    """Respuesta detallada de ruta guardada con pasos"""
    pasos: List[PasoRutaResponse]


class DistanciaResponse(BaseModel):
    """Respuesta de cálculo de distancia entre dos puntos"""
    distancia_km: float
    distancia_formateada: str
    tiempo_caminando_min: int
    tiempo_caminando_formateado: str
    tiempo_bicicleta_min: int
    tiempo_auto_min: int
    desde: Dict[str, float]
    hasta: Dict[str, float]


class PlantillaRutaResponse(BaseModel):
    """Plantilla de ruta predefinida"""
    id: int
    nombre: str
    descripcion: str
    duracion_horas: int
    dificultad: str
    categoria: str
    icono: str
    lugares_sugeridos: List[int]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _formatear_distancia(distancia_km: float) -> str:
    """Formatear distancia para mostrar."""
    if distancia_km < 0.1:
        return f"{int(distancia_km * 1000)} m"
    return f"{distancia_km:.1f} km"


def _formatear_tiempo(tiempo_min: int) -> str:
    """Formatear tiempo para mostrar."""
    if tiempo_min < 60:
        return f"{tiempo_min} min"
    horas = tiempo_min // 60
    minutos = tiempo_min % 60
    if minutos == 0:
        return f"{horas}h"
    return f"{horas}h {minutos}min"


def _obtener_modo_transporte(modo_str: str) -> ModoTransporte:
    """Convertir string a enum ModoTransporte."""
    modos = {
        "walking": ModoTransporte.CAMINANDO,
        "biking": ModoTransporte.BICICLETA,
        "driving": ModoTransporte.AUTO,
        "public": ModoTransporte.TRANSPORTE_PUBLICO
    }
    return modos.get(modo_str.lower(), ModoTransporte.CAMINANDO)


# =====================================================
# ENDPOINTS
# =====================================================

@router.post("/optimizar", response_model=RutaOptimizadaResponse)
async def optimizar_ruta_endpoint(
    request: RutaOptimizarRequest,
    supabase = Depends(get_db)
):
    """
    Optimizar el orden de visita para una lista de lugares.
    
    - Usa algoritmo del vecino más cercano
    - Calcula distancias con fórmula de Haversine (gratuito, sin API)
    - Estima tiempos según modo de transporte
    - Opcional: retornar al punto de inicio
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Obtener datos completos de los lugares
        lugares = []
        for lugar_id in request.lugares_ids:
            lugar = await lugar_repo.get_by_id(lugar_id)
            if lugar:
                lugares.append({
                    'id': lugar.get('id'),
                    'nombre': lugar.get('nombre'),
                    'lat': lugar.get('lat', lugar.get('latitud')),
                    'lng': lugar.get('lng', lugar.get('longitud'))
                })
            else:
                raise NotFoundException(resource_type="Lugar", resource_id=lugar_id)
        
        if not lugares:
            raise ValidationException("No se encontraron lugares válidos")
        
        modo = _obtener_modo_transporte(request.modo)
        
        # Optimizar ruta
        if request.retornar_origen:
            ruta = optimizar_ruta_con_retorno(
                lugares,
                request.origen_lat,
                request.origen_lng,
                modo
            )
        else:
            ruta = optimizar_ruta(
                lugares,
                request.origen_lat,
                request.origen_lng,
                modo
            )
        
        # Construir respuesta
        pasos = []
        for punto in ruta.puntos:
            pasos.append(PasoRutaResponse(
                orden=punto.orden,
                lugar_id=punto.id,
                nombre=punto.nombre,
                lat=punto.lat,
                lng=punto.lng,
                distancia_km=punto.distancia_desde_anterior_km,
                distancia_formateada=_formatear_distancia(punto.distancia_desde_anterior_km),
                tiempo_min=punto.tiempo_desde_anterior_min,
                tiempo_formateado=_formatear_tiempo(punto.tiempo_desde_anterior_min),
                instruccion=punto.instruccion
            ))
        
        return RutaOptimizadaResponse(
            lugares_ordenados=pasos,
            distancia_total_km=round(ruta.distancia_total_km, 2),
            tiempo_total_min=ruta.tiempo_total_min,
            tiempo_formateado=_formatear_tiempo(ruta.tiempo_total_min),
            cantidad_lugares=ruta.cantidad_puntos,
            modo_transporte=request.modo,
            modo_nombre=modo.nombre_es,
            advertencias=ruta.advertencias
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en optimizar_ruta_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guardar", response_model=RutaGuardadaResponse)
async def guardar_ruta(
    request: RutaGuardarRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Guardar una ruta personalizada en el perfil del usuario.
    
    Requiere autenticación.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        # Crear ruta
        ruta_guardada = await ruta_repo.create_route(
            usuario_id=user['id'],
            nombre=request.nombre,
            lugar_ids=request.lugares_ids,
            descripcion=request.descripcion,
            fecha_visita=request.fecha_visita,
            hora_inicio=request.hora_inicio
        )
        
        # Si se solicita compartida, actualizar
        if request.compartida:
            ruta_guardada = await ruta_repo.share_route(ruta_guardada['id'], user['id'])
        
        return RutaGuardadaResponse(
            id=ruta_guardada['id'],
            nombre=ruta_guardada['nombre'],
            descripcion=ruta_guardada.get('descripcion'),
            fecha_visita=ruta_guardada.get('fecha_visita'),
            hora_inicio=ruta_guardada.get('hora_inicio'),
            distancia_total_km=ruta_guardada.get('distancia_total_km', 0),
            tiempo_total_min=ruta_guardada.get('tiempo_estimado_min', 0),
            tiempo_formateado=_formatear_tiempo(ruta_guardada.get('tiempo_estimado_min', 0)),
            cantidad_lugares=len(request.lugares_ids),
            completada=ruta_guardada.get('completada', False),
            compartida=ruta_guardada.get('compartida', False),
            created_at=ruta_guardada.get('created_at')
        )
        
    except Exception as e:
        logger.error(f"Error en guardar_ruta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guardadas", response_model=List[RutaGuardadaResponse])
async def get_rutas_guardadas(
    pagination: PaginationParams = Depends(get_pagination),
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener todas las rutas guardadas por el usuario autenticado.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        rutas = await ruta_repo.get_user_routes(
            usuario_id=user['id'],
            limit=pagination.limit,
            offset=pagination.offset,
            only_active=True
        )
        
        return [
            RutaGuardadaResponse(
                id=r['id'],
                nombre=r['nombre'],
                descripcion=r.get('descripcion'),
                fecha_visita=r.get('fecha_visita'),
                hora_inicio=r.get('hora_inicio'),
                distancia_total_km=r.get('distancia_total_km', 0),
                tiempo_total_min=r.get('tiempo_estimado_min', 0),
                tiempo_formateado=_formatear_tiempo(r.get('tiempo_estimado_min', 0)),
                cantidad_lugares=r.get('cantidad_lugares', 0),
                completada=r.get('completada', False),
                compartida=r.get('compartida', False),
                created_at=r.get('created_at')
            )
            for r in rutas
        ]
        
    except Exception as e:
        logger.error(f"Error en get_rutas_guardadas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guardadas/{ruta_id}", response_model=RutaDetalleResponse)
async def get_ruta_detalle(
    ruta_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Obtener detalle completo de una ruta guardada con todos sus pasos.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        ruta = await ruta_repo.get_route_with_details(ruta_id)
        
        # Verificar propiedad
        if ruta.get('usuario_id') != user['id']:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver esta ruta")
        
        # Construir pasos
        pasos = []
        for detalle in ruta.get('detalles', []):
            pasos.append(PasoRutaResponse(
                orden=detalle.get('orden'),
                lugar_id=detalle.get('lugar_id'),
                nombre=detalle.get('lugar_nombre', 'Lugar'),
                lat=detalle.get('lugar_latitud', 0),
                lng=detalle.get('lugar_longitud', 0),
                distancia_km=detalle.get('distancia_desde_anterior_km', 0),
                distancia_formateada=_formatear_distancia(detalle.get('distancia_desde_anterior_km', 0)),
                tiempo_min=detalle.get('tiempo_estimado_min', 0),
                tiempo_formateado=_formatear_tiempo(detalle.get('tiempo_estimado_min', 0)),
                instruccion=f"Visitar {detalle.get('lugar_nombre', 'el lugar')}"
            ))
        
        return RutaDetalleResponse(
            id=ruta['id'],
            nombre=ruta['nombre'],
            descripcion=ruta.get('descripcion'),
            fecha_visita=ruta.get('fecha_visita'),
            hora_inicio=ruta.get('hora_inicio'),
            distancia_total_km=ruta.get('distancia_total_km', 0),
            tiempo_total_min=ruta.get('tiempo_estimado_min', 0),
            tiempo_formateado=_formatear_tiempo(ruta.get('tiempo_estimado_min', 0)),
            cantidad_lugares=len(pasos),
            completada=ruta.get('completada', False),
            compartida=ruta.get('compartida', False),
            created_at=ruta.get('created_at'),
            pasos=pasos
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_ruta_detalle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/guardadas/{ruta_id}")
async def eliminar_ruta_guardada(
    ruta_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Eliminar una ruta guardada (soft delete).
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        eliminado = await ruta_repo.delete_route(ruta_id, user['id'], soft_delete=True)
        
        if not eliminado:
            raise NotFoundException(resource_type="Ruta", resource_id=ruta_id)
        
        return {"message": "Ruta eliminada correctamente", "ruta_id": ruta_id}
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en eliminar_ruta_guardada: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/guardadas/{ruta_id}/completar")
async def marcar_ruta_completada(
    ruta_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Marcar una ruta como completada.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        ruta = await ruta_repo.mark_route_completed(ruta_id, user['id'])
        
        return {"message": "Ruta marcada como completada", "ruta_id": ruta_id, "completada": True}
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en marcar_ruta_completada: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distancia", response_model=DistanciaResponse)
async def calcular_distancia_endpoint(
    lat1: float = Query(..., description="Latitud origen"),
    lng1: float = Query(..., description="Longitud origen"),
    lat2: float = Query(..., description="Latitud destino"),
    lng2: float = Query(..., description="Longitud destino")
):
    """
    Calcular distancia y tiempos entre dos puntos.
    
    - Distancia en línea recta (fórmula de Haversine)
    - Tiempos estimados por diferentes modos de transporte
    - No requiere API externa (gratuito)
    """
    try:
        distancia = calcular_distancia_haversine(lat1, lng1, lat2, lng2)
        
        tiempos = {
            "walking": calcular_tiempo_estimado(distancia, "walking"),
            "biking": calcular_tiempo_estimado(distancia, "biking"),
            "driving": calcular_tiempo_estimado(distancia, "driving")
        }
        
        return DistanciaResponse(
            distancia_km=round(distancia, 2),
            distancia_formateada=_formatear_distancia(distancia),
            tiempo_caminando_min=tiempos["walking"],
            tiempo_caminando_formateado=_formatear_tiempo(tiempos["walking"]),
            tiempo_bicicleta_min=tiempos["biking"],
            tiempo_auto_min=tiempos["driving"],
            desde={"lat": lat1, "lng": lng1},
            hasta={"lat": lat2, "lng": lng2}
        )
        
    except Exception as e:
        logger.error(f"Error en calcular_distancia_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plantillas", response_model=List[PlantillaRutaResponse])
async def get_plantillas_rutas(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría")
):
    """
    Obtener plantillas de rutas predefinidas.
    
    Útil para sugerir rutas a usuarios nuevos o sin plan.
    """
    try:
        ruta_repo = RutaRepository(None)  # No necesita DB para plantillas
        templates = await ruta_repo.get_route_templates()
        
        if categoria:
            templates = [t for t in templates if t.get('categoria') == categoria]
        
        return [
            PlantillaRutaResponse(
                id=t.get('id'),
                nombre=t.get('nombre'),
                descripcion=t.get('descripcion'),
                duracion_horas=t.get('duracion_horas', 0),
                dificultad=t.get('dificultad', 'fácil'),
                categoria=t.get('categoria'),
                icono=t.get('icono', '🗺️'),
                lugares_sugeridos=t.get('lugares_sugeridos', [])
            )
            for t in templates
        ]
        
    except Exception as e:
        logger.error(f"Error en get_plantillas_rutas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plantillas/{template_id}/aplicar", response_model=RutaGuardadaResponse)
async def aplicar_plantilla_ruta(
    template_id: int,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Aplicar una plantilla de ruta predefinida y guardarla para el usuario.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        templates = await ruta_repo.get_route_templates()
        
        template = next((t for t in templates if t.get('id') == template_id), None)
        
        if not template:
            raise NotFoundException(resource_type="Plantilla", resource_id=template_id)
        
        # Crear ruta desde plantilla
        ruta_guardada = await ruta_repo.create_route(
            usuario_id=user['id'],
            nombre=template.get('nombre'),
            lugar_ids=template.get('lugares_sugeridos', []),
            descripcion=template.get('descripcion')
        )
        
        return RutaGuardadaResponse(
            id=ruta_guardada['id'],
            nombre=ruta_guardada['nombre'],
            descripcion=ruta_guardada.get('descripcion'),
            fecha_visita=ruta_guardada.get('fecha_visita'),
            hora_inicio=ruta_guardada.get('hora_inicio'),
            distancia_total_km=ruta_guardada.get('distancia_total_km', 0),
            tiempo_total_min=ruta_guardada.get('tiempo_estimado_min', 0),
            tiempo_formateado=_formatear_tiempo(ruta_guardada.get('tiempo_estimado_min', 0)),
            cantidad_lugares=len(template.get('lugares_sugeridos', [])),
            completada=ruta_guardada.get('completada', False),
            compartida=ruta_guardada.get('compartida', False),
            created_at=ruta_guardada.get('created_at')
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en aplicar_plantilla_ruta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas")
async def get_rutas_estadisticas(
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """
    Obtener estadísticas de rutas del usuario o globales.
    """
    try:
        ruta_repo = RutaRepository(supabase)
        
        if user:
            # Estadísticas del usuario
            rutas = await ruta_repo.get_user_routes(user['id'], limit=1000)
            total = len(rutas)
            completadas = sum(1 for r in rutas if r.get('completada'))
            compartidas = sum(1 for r in rutas if r.get('compartida'))
            
            return {
                "usuario_id": user['id'],
                "total_rutas": total,
                "rutas_completadas": completadas,
                "tasa_completacion": round((completadas / total * 100), 1) if total > 0 else 0,
                "rutas_compartidas": compartidas
            }
        else:
            # Estadísticas globales
            return await ruta_repo.get_route_stats()
        
    except Exception as e:
        logger.error(f"Error en get_rutas_estadisticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_rutas_info():
    """Obtener información sobre el servicio de rutas."""
    return {
        "servicio": "Rutas - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para optimización y gestión de rutas turísticas",
        "endpoints_disponibles": [
            "POST /rutas/optimizar",
            "POST /rutas/guardar",
            "GET /rutas/guardadas",
            "GET /rutas/guardadas/{id}",
            "DELETE /rutas/guardadas/{id}",
            "PUT /rutas/guardadas/{id}/completar",
            "GET /rutas/distancia",
            "GET /rutas/plantillas",
            "POST /rutas/plantillas/{id}/aplicar",
            "GET /rutas/estadisticas",
            "GET /rutas/info"
        ],
        "modos_transporte": [
            {"value": "walking", "label": "Caminando", "velocidad_kmh": 5},
            {"value": "biking", "label": "Bicicleta", "velocidad_kmh": 15},
            {"value": "driving", "label": "Auto", "velocidad_kmh": 30}
        ],
        "algoritmo": "Vecino más cercano (Nearest Neighbor)",
        "gratuito": True,
        "sin_api_externa": True
    }