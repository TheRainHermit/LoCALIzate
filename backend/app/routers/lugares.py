"""
Endpoints para Lugares Turísticos - LoCALIzate Backend
======================================================

Proporciona endpoints para gestionar lugares turísticos en Cali:
    - Listado de lugares con filtros (interés, rating, precio, búsqueda)
    - Detalle de lugar específico
    - Lugares cercanos por geolocalización
    - Lugares destacados
    - Recomendaciones personalizadas
    - Reseñas y calificaciones de lugares

Dependencias:
    - LugarRepository: Acceso a datos de lugares
    - RecommendationService: Recomendaciones personalizadas
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.repositories.lugar_repo import LugarRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.services.recommendation import recommendation_service
from app.core.database import get_db
from app.core.dependencies import (
    get_current_user_optional, 
    get_pagination, 
    PaginationParams,
    get_lugar_filters,
    LugarFilters
)
from app.core.exceptions import NotFoundException, ValidationException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lugares", tags=["Lugares Turísticos"])


# =====================================================
# PYDANTIC MODELS
# =====================================================

class LugarResponse(BaseModel):
    """Respuesta básica para un lugar turístico"""
    id: int
    nombre: str
    descripcion_corta: Optional[str] = None
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    barrio: Optional[str] = None
    interes: str
    icono: str
    rating: float
    rating_count: int = 0
    horario: Optional[str] = None
    precio: Optional[str] = None
    imagen: Optional[str] = None
    destacado: bool = False
    
    class Config:
        from_attributes = True


class LugarDetalleResponse(LugarResponse):
    """Respuesta detallada para un lugar turístico"""
    descripcion: str
    precio_min: Optional[int] = None
    precio_max: Optional[int] = None
    telefono: Optional[str] = None
    sitio_web: Optional[str] = None
    instagram: Optional[str] = None
    email: Optional[str] = None
    imagenes: Optional[List[str]] = None
    video_url: Optional[str] = None
    tip_caleño: Optional[str] = None
    historia: Optional[str] = None
    datos_curiosos: Optional[List[str]] = None
    verificado: bool = False
    created_at: str
    updated_at: Optional[str] = None
    
    # Campos calculados
    rating_stars: str = ""
    precio_formateado: str = ""


class LugarListResponse(BaseModel):
    """Respuesta para listado de lugares"""
    total: int
    limit: int
    offset: int
    results: List[LugarResponse]


class LugarCercanoResponse(LugarResponse):
    """Respuesta para lugar cercano con distancia"""
    distancia_km: float
    distancia_formateada: str
    tiempo_estimado_min: int


class RecomendacionResponse(BaseModel):
    """Respuesta para recomendación de lugar"""
    id: int
    nombre: str
    puntaje: float
    razon: str
    categoria: str
    rating: float
    distancia_km: Optional[float] = None


class ResenaResponse(BaseModel):
    """Respuesta para reseña de usuario"""
    id: int
    usuario_id: str
    usuario_nombre: Optional[str] = None
    usuario_avatar: Optional[str] = None
    rating: int
    comentario: Optional[str] = None
    fotos: Optional[List[str]] = None
    created_at: str


class ResenaCreateRequest(BaseModel):
    """Request para crear una reseña"""
    rating: int = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comentario: Optional[str] = Field(None, max_length=500)
    fotos: Optional[List[str]] = None


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _calcular_rating_stars(rating: float) -> str:
    """Calcular representación visual del rating."""
    full = int(rating)
    half = rating - full >= 0.5
    empty = 5 - full - (1 if half else 0)
    return "★" * full + ("½" if half else "") + "☆" * empty


def _formatear_precio(precio_min: Optional[int], precio_max: Optional[int], precio_texto: Optional[str]) -> str:
    """Formatear precio para mostrar."""
    if precio_min and precio_max:
        if precio_min == precio_max:
            return f"${precio_min:,} COP".replace(",", ".")
        return f"${precio_min:,} - ${precio_max:,} COP".replace(",", ".")
    elif precio_min:
        return f"Desde ${precio_min:,} COP".replace(",", ".")
    elif precio_max:
        return f"Hasta ${precio_max:,} COP".replace(",", ".")
    return precio_texto or "Consultar"


def _formatear_distancia(distancia_km: float) -> str:
    """Formatear distancia para mostrar."""
    if distancia_km < 0.1:
        return f"{int(distancia_km * 1000)} m"
    return f"{distancia_km:.1f} km"


def _convertir_lugar_response(lugar: Dict[str, Any], incluir_detalles: bool = False) -> dict:
    """Convertir lugar de BD a diccionario de respuesta."""
    resultado = {
        "id": lugar.get('id'),
        "nombre": lugar.get('nombre'),
        "descripcion_corta": lugar.get('descripcion_corta'),
        "latitud": lugar.get('lat', lugar.get('latitud')),
        "longitud": lugar.get('lng', lugar.get('longitud')),
        "direccion": lugar.get('direccion'),
        "barrio": lugar.get('barrio'),
        "interes": lugar.get('interes'),
        "icono": lugar.get('icono', '📍'),
        "rating": lugar.get('rating', 0),
        "rating_count": lugar.get('rating_count', 0),
        "horario": lugar.get('horario'),
        "precio": lugar.get('precio'),
        "imagen": lugar.get('imagen', lugar.get('imagen_principal')),
        "destacado": lugar.get('destacado', False)
    }
    
    if incluir_detalles:
        resultado.update({
            "descripcion": lugar.get('descripcion', ''),
            "precio_min": lugar.get('precio_min'),
            "precio_max": lugar.get('precio_max'),
            "telefono": lugar.get('telefono'),
            "sitio_web": lugar.get('sitio_web'),
            "instagram": lugar.get('instagram'),
            "email": lugar.get('email'),
            "imagenes": lugar.get('imagenes', []),
            "video_url": lugar.get('video_url'),
            "tip_caleño": lugar.get('tip_caleño'),
            "historia": lugar.get('historia'),
            "datos_curiosos": lugar.get('datos_curiosos', []),
            "verificado": lugar.get('verificado', False),
            "created_at": lugar.get('created_at'),
            "updated_at": lugar.get('updated_at'),
            "rating_stars": _calcular_rating_stars(lugar.get('rating', 0)),
            "precio_formateado": _formatear_precio(
                lugar.get('precio_min'),
                lugar.get('precio_max'),
                lugar.get('precio')
            )
        })
    
    return resultado


# =====================================================
# ENDPOINTS PÚBLICOS
# =====================================================

@router.get("/", response_model=LugarListResponse)
async def listar_lugares(
    filters: LugarFilters = Depends(get_lugar_filters),
    pagination: PaginationParams = Depends(get_pagination),
    supabase = Depends(get_db)
):
    """
    Listar lugares turísticos con filtros opcionales.
    
    Filtros disponibles:
    - interes: cultura, naturaleza, gastronomia, salsa, aventura
    - busqueda: texto en nombre o descripción
    - min_rating: rating mínimo (0-5)
    - max_precio: precio máximo
    - destacados: solo lugares destacados
    - lat/lng/radio_km: búsqueda por proximidad
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Construir filtros base
        base_filters = {"activo": True}
        
        if filters.interes:
            base_filters["interes"] = filters.interes.value if hasattr(filters.interes, 'value') else filters.interes
        
        if hasattr(filters, 'destacado') and filters.destacado is not None:
            base_filters["destacado"] = filters.destacado
        
        # Si hay búsqueda por proximidad
        if filters.has_location:
            lugares = await lugar_repo.get_nearby(
                lat=filters.lat,
                lng=filters.lng,
                radio_km=filters.radio_km,
                interes=filters.interes.value if filters.interes and hasattr(filters.interes, 'value') else filters.interes,
                limit=pagination.limit
            )
            
            # Convertir para respuesta
            resultados = []
            for lugar in lugares:
                lugar_response = _convertir_lugar_response(lugar)
                resultados.append(LugarResponse(**lugar_response))
            
            return LugarListResponse(
                total=len(resultados),
                limit=pagination.limit,
                offset=pagination.offset,
                results=resultados
            )
        
        # Búsqueda por texto
        if filters.has_search:
            lugares = await lugar_repo.search_lugares(
                search_term=filters.busqueda,
                interes=filters.interes.value if filters.interes and hasattr(filters.interes, 'value') else filters.interes,
                limit=pagination.limit,
                offset=pagination.offset
            )
        else:
            # Filtros adicionales
            if filters.min_rating:
                lugares = await lugar_repo.get_by_rating(
                    min_rating=filters.min_rating,
                    limit=pagination.limit,
                    offset=pagination.offset
                )
            else:
                lugares = await lugar_repo.get_all(
                    filters=base_filters,
                    limit=pagination.limit,
                    offset=pagination.offset,
                    order_by="rating",
                    order_desc=True
                )
        
        # Obtener total
        total = await lugar_repo.get_count(filters=base_filters)
        
        resultados = []
        for lugar in lugares:
            lugar_response = _convertir_lugar_response(lugar)
            resultados.append(LugarResponse(**lugar_response))
        
        return LugarListResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            results=resultados
        )
        
    except Exception as e:
        logger.error(f"Error en listar_lugares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/destacados", response_model=List[LugarResponse])
async def get_lugares_destacados(
    limit: int = Query(6, ge=1, le=20, description="Número de lugares destacados"),
    supabase = Depends(get_db)
):
    """Obtener lugares turísticos destacados."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        lugares = await lugar_repo.get_destacados(limit=limit)
        
        resultados = []
        for lugar in lugares:
            lugar_response = _convertir_lugar_response(lugar)
            resultados.append(LugarResponse(**lugar_response))
        
        return resultados
        
    except Exception as e:
        logger.error(f"Error en get_lugares_destacados: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/populares", response_model=List[LugarResponse])
async def get_lugares_populares(
    limit: int = Query(10, ge=1, le=30, description="Número de lugares populares"),
    supabase = Depends(get_db)
):
    """Obtener lugares más populares (mayor rating y cantidad de reseñas)."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        lugares = await lugar_repo.get_popular(limit=limit)
        
        resultados = []
        for lugar in lugares:
            lugar_response = _convertir_lugar_response(lugar)
            resultados.append(LugarResponse(**lugar_response))
        
        return resultados
        
    except Exception as e:
        logger.error(f"Error en get_lugares_populares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gratis", response_model=List[LugarResponse])
async def get_lugares_gratis(
    limit: int = Query(20, ge=1, le=50, description="Número de lugares gratis"),
    supabase = Depends(get_db)
):
    """Obtener lugares gratuitos para visitar."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        lugares = await lugar_repo.get_gratis(limit=limit)
        
        resultados = []
        for lugar in lugares:
            lugar_response = _convertir_lugar_response(lugar)
            resultados.append(LugarResponse(**lugar_response))
        
        return resultados
        
    except Exception as e:
        logger.error(f"Error en get_lugares_gratis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cercanos", response_model=List[LugarCercanoResponse])
async def get_lugares_cercanos(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del usuario"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud del usuario"),
    radio_km: float = Query(2.0, ge=0.5, le=10, description="Radio de búsqueda en km"),
    interes: Optional[str] = Query(None, description="Filtrar por interés"),
    limit: int = Query(20, ge=1, le=50, description="Número de resultados"),
    supabase = Depends(get_db)
):
    """
    Encontrar lugares cercanos a una ubicación.
    """
    try:
        from app.services.optimizador_rutas import calcular_tiempo_estimado
        
        lugar_repo = LugarRepository(supabase)
        
        lugares = await lugar_repo.get_nearby(
            lat=lat,
            lng=lng,
            radio_km=radio_km,
            interes=interes,
            limit=limit
        )
        
        resultados = []
        for lugar in lugares:
            distancia = lugar.get('distancia_km', 0)
            tiempo = calcular_tiempo_estimado(distancia, "walking")
            
            lugar_response = _convertir_lugar_response(lugar)
            
            resultados.append(LugarCercanoResponse(
                **lugar_response,
                distancia_km=distancia,
                distancia_formateada=_formatear_distancia(distancia),
                tiempo_estimado_min=tiempo
            ))
        
        return resultados
        
    except Exception as e:
        logger.error(f"Error en get_lugares_cercanos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intereses", response_model=List[Dict[str, str]])
async def get_intereses_disponibles():
    """Obtener lista de intereses/categorías disponibles."""
    from app.models.lugar import get_intereses_list
    return get_intereses_list()


@router.get("/recomendaciones", response_model=List[RecomendacionResponse])
async def get_recomendaciones_lugares(
    lat: Optional[float] = Query(None, description="Latitud del usuario"),
    lng: Optional[float] = Query(None, description="Longitud del usuario"),
    interes: Optional[str] = Query(None, description="Interés específico"),
    limit: int = Query(10, ge=1, le=20),
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """
    Obtener recomendaciones personalizadas de lugares.
    
    - Si usuario autenticado: basado en sus intereses
    - Si se proporciona interés: filtrar por ese interés
    - Si se proporciona ubicación: priorizar cercanía
    """
    try:
        lugar_repo = LugarRepository(supabase)
        
        if interes:
            # Recomendar por interés específico
            recomendaciones = await recommendation_service.recomendar_por_interes(
                lugar_repo, interes, limit=limit
            )
        elif user:
            # Usuario autenticado: recomendaciones personalizadas
            usuario_repo = UsuarioRepository(supabase)
            recomendaciones = await recommendation_service.recomendar_por_intereses_usuario(
                usuario_repo, lugar_repo, user['id'], limit=limit
            )
        else:
            # Usuario anónimo: lugares populares
            recomendaciones = await recommendation_service.recomendar_populares(
                lugar_repo, limit=limit
            )
        
        return [RecomendacionResponse(**r.to_dict()) for r in recomendaciones]
        
    except Exception as e:
        logger.error(f"Error en get_recomendaciones_lugares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similares/{lugar_id}", response_model=List[RecomendacionResponse])
async def get_lugares_similares(
    lugar_id: int,
    limit: int = Query(5, ge=1, le=10),
    supabase = Depends(get_db)
):
    """Obtener lugares similares a uno dado."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        recomendaciones = await recommendation_service.recomendar_similares(
            lugar_repo, lugar_id, limit=limit
        )
        
        return [RecomendacionResponse(**r.to_dict()) for r in recomendaciones]
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_lugares_similares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lugar_id}", response_model=LugarDetalleResponse)
async def get_lugar_detalle(
    lugar_id: int,
    supabase = Depends(get_db)
):
    """Obtener detalle completo de un lugar turístico."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        lugar = await lugar_repo.get_by_id(lugar_id)
        
        if not lugar:
            raise NotFoundException(
                resource_type="Lugar",
                resource_id=lugar_id
            )
        
        lugar_response = _convertir_lugar_response(lugar, incluir_detalles=True)
        
        return LugarDetalleResponse(**lugar_response)
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_lugar_detalle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ENDPOINTS DE RESEÑAS
# =====================================================

@router.get("/{lugar_id}/resenas", response_model=List[ResenaResponse])
async def get_resenas_lugar(
    lugar_id: int,
    supabase = Depends(get_db)
):
    """Obtener reseñas de usuarios para un lugar."""
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Verificar que el lugar existe
        lugar = await lugar_repo.get_by_id(lugar_id)
        if not lugar:
            raise NotFoundException(resource_type="Lugar", resource_id=lugar_id)
        
        # Obtener reseñas
        result = supabase.table("resenas").select(
            "*, perfiles(nombre, avatar_url)"
        ).eq("lugar_id", lugar_id).eq("activa", True).order("created_at", desc=True).execute()
        
        resenas = []
        for r in (result.data or []):
            perfil = r.get("perfiles", {})
            resenas.append(ResenaResponse(
                id=r['id'],
                usuario_id=r['usuario_id'],
                usuario_nombre=perfil.get('nombre'),
                usuario_avatar=perfil.get('avatar_url'),
                rating=r['rating'],
                comentario=r.get('comentario'),
                fotos=r.get('fotos', []),
                created_at=r['created_at']
            ))
        
        return resenas
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en get_resenas_lugar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lugar_id}/resenas", response_model=ResenaResponse)
async def crear_resena_lugar(
    lugar_id: int,
    resena_data: ResenaCreateRequest,
    supabase = Depends(get_db),
    user: dict = Depends(get_current_user_optional)
):
    """
    Crear una reseña para un lugar (requiere autenticación).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Se requiere autenticación para escribir reseñas")
    
    try:
        lugar_repo = LugarRepository(supabase)
        
        # Verificar que el lugar existe
        lugar = await lugar_repo.get_by_id(lugar_id)
        if not lugar:
            raise NotFoundException(resource_type="Lugar", resource_id=lugar_id)
        
        # Verificar si el usuario ya reseñó este lugar
        existing = supabase.table("resenas").select("id").eq(
            "usuario_id", user['id']
        ).eq("lugar_id", lugar_id).execute()
        
        if existing.data and len(existing.data) > 0:
            raise ValidationException("Ya has escrito una reseña para este lugar")
        
        # Crear reseña
        resena_data_insert = {
            "usuario_id": user['id'],
            "lugar_id": lugar_id,
            "rating": resena_data.rating,
            "comentario": resena_data.comentario,
            "fotos": resena_data.fotos,
            "activa": True,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("resenas").insert(resena_data_insert).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Error al crear la reseña")
        
        nueva_resena = result.data[0]
        
        # Actualizar rating del lugar (el trigger de BD lo hará automáticamente)
        
        return ResenaResponse(
            id=nueva_resena['id'],
            usuario_id=nueva_resena['usuario_id'],
            usuario_nombre=user.get('nombre', 'Usuario'),
            usuario_avatar=user.get('avatar_url'),
            rating=nueva_resena['rating'],
            comentario=nueva_resena.get('comentario'),
            fotos=nueva_resena.get('fotos', []),
            created_at=nueva_resena['created_at']
        )
        
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en crear_resena_lugar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# INFO ENDPOINT
# =====================================================

@router.get("/info")
async def get_lugares_info():
    """Obtener información sobre el servicio de lugares."""
    from app.models.lugar import get_intereses_list
    
    return {
        "servicio": "Lugares Turísticos - LoCALIzate",
        "version": "1.0.0",
        "descripcion": "Endpoints para lugares turísticos de Cali",
        "endpoints_disponibles": [
            "GET /lugares/",
            "GET /lugares/destacados",
            "GET /lugares/populares",
            "GET /lugares/gratis",
            "GET /lugares/cercanos",
            "GET /lugares/intereses",
            "GET /lugares/recomendaciones",
            "GET /lugares/similares/{id}",
            "GET /lugares/{id}",
            "GET /lugares/{id}/resenas",
            "POST /lugares/{id}/resenas",
            "GET /lugares/info"
        ],
        "intereses_disponibles": get_intereses_list(),
        "filtros_disponibles": [
            "interes",
            "busqueda",
            "min_rating",
            "max_precio",
            "destacados",
            "lat/lng/radio_km"
        ]
    }